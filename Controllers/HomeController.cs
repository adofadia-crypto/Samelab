using Microsoft.AspNetCore.Mvc;
using SamelabWeb.Models;
using Microsoft.Data.SqlClient;
using System.Diagnostics;

namespace SamelabWeb.Controllers
{
    public class HomeController : Controller
    {
        private readonly string _connectionString;

        public HomeController(IConfiguration configuration)
        {
            _connectionString = configuration.GetConnectionString("DefaultConnection");
        }

        public IActionResult Index()
        {
            // Variables para los 3 niveles de la gráfica
            int highCount = 0;
            int mediumCount = 0;
            int lowCount = 0;
            var listaEmpleados = new List<EmpleadoResultado>();

            using (var conn = new SqlConnection(_connectionString))
            {
                try
                {
                    conn.Open();

                    // 1. Contar por Niveles de Riesgo (IA Dashboard)
                    var cmdContar = new SqlCommand("SELECT RiskLevel, COUNT(*) FROM empleados_visualizacion GROUP BY RiskLevel", conn);
                    using (var reader = cmdContar.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            string risk = reader[0]?.ToString()?.Trim() ?? "Low";
                            int cantidad = Convert.ToInt32(reader[1]);

                            if (risk.Equals("High", StringComparison.OrdinalIgnoreCase)) highCount = cantidad;
                            else if (risk.Equals("Medium", StringComparison.OrdinalIgnoreCase)) mediumCount = cantidad;
                            else if (risk.Equals("Low", StringComparison.OrdinalIgnoreCase)) lowCount = cantidad;
                        }
                    }

                    // 2. Traer lista desde la capa de ORO (Visualización)
                    var cmdLista = new SqlCommand("SELECT TOP 20 Department, JobRole, RiskLevel, AttritionProbability FROM empleados_visualizacion", conn);

                    using (var reader = cmdLista.ExecuteReader())
                    {
                        int idSimulado = 1;
                        while (reader.Read())
                        {
                            listaEmpleados.Add(new EmpleadoResultado
                            {
                                id = idSimulado.ToString(),
                                Department = reader["Department"]?.ToString() ?? "N/A",
                                JobRole = reader["JobRole"]?.ToString() ?? "N/A",

                                // MAPEO: RiskLevel de Python -> Prediction de C#
                                Prediction = reader["RiskLevel"] != DBNull.Value ? reader["RiskLevel"].ToString() : "Pendiente",

                                // Probabilidad de riesgo en formato porcentaje
                                Probability = reader["AttritionProbability"] != DBNull.Value ?
                                              Math.Round(Convert.ToDouble(reader["AttritionProbability"]) * 100, 2) : 0
                            });
                            idSimulado++;
                        }
                    }
                }
                catch (Exception ex)
                {
                    Debug.WriteLine("Error al leer de Azure: " + ex.Message);
                }
            }

            // Pasamos los datos a la vista (Dona de 3 colores)
            ViewBag.High = highCount;
            ViewBag.Medium = mediumCount;
            ViewBag.Low = lowCount;

            return View(listaEmpleados);
        }

        [HttpPost]
        public IActionResult SubirCSV(IFormFile archivo)
        {
            if (archivo != null && archivo.Length > 0)
            {
                using (var reader = new StreamReader(archivo.OpenReadStream()))
                {
                    reader.ReadLine(); // Saltar cabecera

                    using (var conn = new SqlConnection(_connectionString))
                    {
                        conn.Open();
                        using (var cleanCmd = new SqlCommand("TRUNCATE TABLE empleados", conn))
                        {
                            cleanCmd.ExecuteNonQuery();
                        }

                        while (!reader.EndOfStream)
                        {
                            var linea = reader.ReadLine();
                            if (string.IsNullOrWhiteSpace(linea)) continue;
                            var valores = linea.Split(',');

                            // Insertamos las 35 columnas originales del dataset IBM
                            string sql = @"INSERT INTO empleados (Age, Attrition, BusinessTravel, DailyRate, Department, DistanceFromHome, Education, EducationField, EmployeeCount, EmployeeNumber, EnvironmentSatisfaction, Gender, HourlyRate, JobInvolvement, JobLevel, JobRole, JobSatisfaction, MaritalStatus, MonthlyIncome, MonthlyRate, NumCompaniesWorked, Over18, OverTime, PercentSalaryHike, PerformanceRating, RelationshipSatisfaction, StandardHours, StockOptionLevel, TotalWorkingYears, TrainingTimesLastYear, WorkLifeBalance, YearsAtCompany, YearsInCurrentRole, YearsSinceLastPromotion, YearsWithCurrManager) 
                                           VALUES (@p1, @p2, @p3, @p4, @p5, @p6, @p7, @p8, @p9, @p10, @p11, @p12, @p13, @p14, @p15, @p16, @p17, @p18, @p19, @p20, @p21, @p22, @p23, @p24, @p25, @p26, @p27, @p28, @p29, @p30, @p31, @p32, @p33, @p34, @p35)";

                            using (var cmd = new SqlCommand(sql, conn))
                            {
                                for (int i = 0; i < 35; i++)
                                {
                                    cmd.Parameters.AddWithValue($"@p{i + 1}", (object)valores[i] ?? DBNull.Value);
                                }
                                cmd.ExecuteNonQuery();
                            }
                        }
                    }
                }
            }
            return RedirectToAction("Index");
        }

        [HttpPost]
        public IActionResult EjecutarIA()
        {
            // 1. Limpia datos
            EjecutarScriptPython("IA/limpiar_datos.py");

            // 2. Ejecuta el modelo
            EjecutarScriptPython("IA/predict.py");

            // 3. NUEVO: Genera las gráficas para la vista
            EjecutarScriptPython("IA/generar_graficas.py");

            return RedirectToAction("Index");
        }

        private void EjecutarScriptPython(string nombreScriptRelativo)
        {
            try
            {
                string rootPath = AppContext.BaseDirectory;

                // Ajuste de ruta para entorno de desarrollo (Mac)
                if (rootPath.Contains("bin"))
                {
                    rootPath = Path.GetFullPath(Path.Combine(rootPath, "..", "..", ".."));
                }

                string fullPathScript = Path.Combine(rootPath, nombreScriptRelativo);
                string pythonExecutable = "python3";

                // Si existe el venv (Tu Mac), lo priorizamos
                string venvPath = Path.Combine(rootPath, "IA", "venv", "bin", "python3");
                if (System.IO.File.Exists(venvPath))
                {
                    pythonExecutable = venvPath;
                }

                ProcessStartInfo start = new ProcessStartInfo();
                start.FileName = pythonExecutable;
                start.Arguments = $"\"{fullPathScript}\"";
                start.UseShellExecute = false;
                start.RedirectStandardError = true;
                start.RedirectStandardOutput = true;
                start.CreateNoWindow = true;
                start.WorkingDirectory = Path.Combine(rootPath, "IA");

                // --- AJUSTE PARA AZURE: Inyectar rutas de librerías instaladas por SSH ---
                // Esto le dice a Python que busque en /home/.local/lib...
                string azureLibPath = "/home/.local/lib/python3.11/site-packages";
                if (System.IO.Directory.Exists(azureLibPath))
                {
                    start.EnvironmentVariables["PYTHONPATH"] = azureLibPath;
                    start.EnvironmentVariables["PATH"] = "/home/.local/bin:" + Environment.GetEnvironmentVariable("PATH");
                }
                // -----------------------------------------------------------------------

                using (Process process = Process.Start(start))
                {
                    if (process != null)
                    {
                        string output = process.StandardOutput.ReadToEnd();
                        string error = process.StandardError.ReadToEnd();

                        // Timeout de 3 minutos para procesos pesados de IA
                        bool finished = process.WaitForExit(180000);

                        if (!finished)
                        {
                            process.Kill();
                            Console.WriteLine("Error: El script de Python superó el tiempo de espera.");
                        }

                        if (!string.IsNullOrEmpty(error))
                        {
                            Console.WriteLine("Error Python: " + error);
                        }
                        Console.WriteLine("Salida Python: " + output);
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error en script: " + ex.Message);
            }
        }
    }

    public class EmpleadoResultado
    {
        public string id { get; set; }
        public string Department { get; set; }
        public string JobRole { get; set; }
        public string Prediction { get; set; } // Mostrará High, Medium o Low
        public double Probability { get; set; } // El porcentaje de riesgo
    }
}