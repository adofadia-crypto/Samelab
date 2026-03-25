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
            int siCount = 0;
            int noCount = 0;
            var listaEmpleados = new List<EmpleadoResultado>();

            using (var conn = new SqlConnection(_connectionString))
            {
                try
                {
                    conn.Open();

                    // 1. Contar para la gráfica (SQL Server)
                    var cmdContar = new SqlCommand("SELECT Prediccion, COUNT(*) FROM empleados_visualizacion WHERE Prediccion IS NOT NULL GROUP BY Prediccion", conn);
                    using (var reader = cmdContar.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            string pred = reader[0].ToString(); // "Sí" o "No"
                            if (pred == "1") siCount = Convert.ToInt32(reader[1]);
                            else if (pred == "0") noCount = Convert.ToInt32(reader[1]);
                        }
                    }

                    // 2. Traer lista (SQL Server usa TOP en lugar de LIMIT)
                    var cmdLista = new SqlCommand("SELECT TOP 20 Department, JobRole, Prediccion FROM empleados_visualizacion WHERE Prediccion IS NOT NULL", conn);
                    using (var reader = cmdLista.ExecuteReader())
                    {
                        int idSimulado = 1;
                        while (reader.Read())
                        {
                            listaEmpleados.Add(new EmpleadoResultado
                            {
                                id = idSimulado.ToString(),
                                Department = reader["Department"].ToString(),
                                JobRole = reader["JobRole"].ToString(),
                                Prediction = reader["Prediccion"] != DBNull.Value ? reader["Prediccion"].ToString() : "Pendiente"
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

            ViewBag.Si = siCount;
            ViewBag.No = noCount;
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
                        // En SQL Server TRUNCATE funciona igual, pero usamos SqlCommand
                        using (var cleanCmd = new SqlCommand("TRUNCATE TABLE empleados", conn))
                        {
                            cleanCmd.ExecuteNonQuery();
                        }

                        while (!reader.EndOfStream)
                        {
                            var linea = reader.ReadLine();
                            if (string.IsNullOrWhiteSpace(linea)) continue;
                            var valores = linea.Split(',');

                            string sql = @"INSERT INTO empleados (Age, Attrition, BusinessTravel, DailyRate, Department, DistanceFromHome, Education, EducationField, EmployeeCount, EmployeeNumber, EnvironmentSatisfaction, Gender, HourlyRate, JobInvolvement, JobLevel, JobRole, JobSatisfaction, MaritalStatus, MonthlyIncome, MonthlyRate, NumCompaniesWorked, Over18, OverTime, PercentSalaryHike, PerformanceRating, RelationshipSatisfaction, StandardHours, StockOptionLevel, TotalWorkingYears, TrainingTimesLastYear, WorkLifeBalance, YearsAtCompany, YearsInCurrentRole, YearsSinceLastPromotion, YearsWithCurrManager) 
                                           VALUES (@p1, @p2, @p3, @p4, @p5, @p6, @p7, @p8, @p9, @p10, @p11, @p12, @p13, @p14, @p15, @p16, @p17, @p18, @p19, @p20, @p21, @p22, @p23, @p24, @p25, @p26, @p27, @p28, @p29, @p30, @p31, @p32, @p33, @p34, @p35)";

                            using (var cmd = new SqlCommand(sql, conn))
                            {
                                for (int i = 0; i < 35; i++)
                                {
                                    // Azure SQL prefiere valores limpios, añadimos una validación simple
                                    cmd.Parameters.AddWithValue($"@p{i + 1}", valores[i] ?? (object)DBNull.Value);
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
            EjecutarScriptPython("IA/limpiar_datos.py");
            EjecutarScriptPython("IA/predict.py");
            EjecutarScriptPython("IA/generar_graficas.py");
            return RedirectToAction("Index");
        }

        private void EjecutarScriptPython(string rutaScript)
        {
            try
            {
                string homeSite = Environment.GetEnvironmentVariable("HOME") ?? ".";
                string fullPath = Path.Combine(homeSite, "site/wwwroot", rutaScript);

                ProcessStartInfo start = new ProcessStartInfo();
                start.FileName = "python3"; // En Azure Linux esto es correcto
                start.Arguments = fullPath;
                start.UseShellExecute = false;
                start.RedirectStandardError = true;
                start.RedirectStandardOutput = true;
                start.CreateNoWindow = true;

                using (Process process = Process.Start(start))
                {
                    process.WaitForExit(120000);
                    string stdout = process.StandardOutput.ReadToEnd();
                    string stderr = process.StandardError.ReadToEnd();
                    process.WaitForExit();
                    // Esto saldrá en tu Log Stream si algo falla
                    if (!string.IsNullOrEmpty(stderr)) Console.WriteLine("Error en " + rutaScript + ": " + stderr);
                }
            }
            catch (Exception ex) { Console.WriteLine("Fallo ejecución: " + ex.Message); }
        }
    }

    public class EmpleadoResultado
    {
        public string id { get; set; }
        public string Department { get; set; }
        public string JobRole { get; set; }
        public string Prediction { get; set; }
    }
}