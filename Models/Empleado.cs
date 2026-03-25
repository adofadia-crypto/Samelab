using System.ComponentModel.DataAnnotations;

namespace SamelabWeb.Models
{
    public class Empleado
    {
        [Key]
        public int Id { get; set; }
        public int Age { get; set; }
        public string Attrition { get; set; }
        public string BusinessTravel { get; set; }
        public int DailyRate { get; set; }
        public string Department { get; set; }
        public int DistanceFromHome { get; set; }
        public int Education { get; set; }
        public string EducationField { get; set; }
        public int EmployeeCount { get; set; }
        public int EmployeeNumber { get; set; }
        public int EnvironmentSatisfaction { get; set; }
        public string Gender { get; set; }
        public int HourlyRate { get; set; }
        public int JobInvolvement { get; set; }
        public int JobLevel { get; set; }
        public string JobRole { get; set; }
        public int JobSatisfaction { get; set; }
        public string MaritalStatus { get; set; }
        public int MonthlyIncome { get; set; }
        public int MonthlyRate { get; set; }
        public int NumCompaniesWorked { get; set; }
        public string Over18 { get; set; }
        public string OverTime { get; set; }
        public int PercentSalaryHike { get; set; }
        public int PerformanceRating { get; set; }
        public int RelationshipSatisfaction { get; set; }
        public int StandardHours { get; set; }
        public int StockOptionLevel { get; set; }
        public int TotalWorkingYears { get; set; }
        public int TrainingTimesLastYear { get; set; }
        public int WorkLifeBalance { get; set; }
        public int YearsAtCompany { get; set; }
        public int YearsInCurrentRole { get; set; }
        public int YearsSinceLastPromotion { get; set; }
        public int YearsWithCurrManager { get; set; }
        public string Prediction { get; set; }
    }
}