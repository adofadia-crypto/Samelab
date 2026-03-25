using Microsoft.EntityFrameworkCore;
using SamelabWeb.Models;

namespace SamelabWeb.Models
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options)
        {
        }

        // Este DbSet representa tu tabla de Azure
        public DbSet<Empleado> empleados { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);
            // Esto asegura que Entity Framework busque la tabla "empleados" exactamente como la creamos en SQL
            modelBuilder.Entity<Empleado>().ToTable("empleados");
        }
    }
}