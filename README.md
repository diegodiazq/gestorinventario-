# GestorInventario (proyecto listo)

## Requisitos
- Python 3.9+
- Visual Studio Code (opcional)
- Microsoft ODBC Driver 17 for SQL Server
- Base de datos SQL Server llamada `Gestor_inventario`
  (usa el script proporcionado por el usuario)

## Instalar dependencias
```bash
python -m venv venv
# activar el venv (Windows PowerShell)
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Ejecutar
```bash
python app.py
```
Abre http://127.0.0.1:5000 en el navegador.

## Notas
- La conexión está configurada a `DESKTOP-E26QEMQ\SQLEXPRESS` con Trusted_Connection (autenticación Windows).
- Si tu SQL Server usa otro método de autenticación, edita `db_config.py`.
