# app.py
from flask import Flask, render_template, request, jsonify
import sqlanydb
import os

app = Flask(__name__)

# Database connection parameters from environment variables
DB_CONFIG = {
    "userid": os.environ.get("DB_USER", "supervisortopuid"),
    "password": os.environ.get("DB_PASSWORD", "thisisthetopuserlevelpwd"),
    "host": os.environ.get("DB_HOST", "103.118.151.42"),
    "dbn": os.environ.get("DB_NAME", "gm2024")
}


def get_db_connection():
    """Establish connection to SQL Anywhere database"""
    try:
        conn = sqlanydb.connect(
            userid=DB_CONFIG["userid"],
            password=DB_CONFIG["password"],
            host=DB_CONFIG["host"],
            dbn=DB_CONFIG["dbn"]
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/sales')
def sales():
    """Display full sales details"""
    try:
        # Connect to database
        conn = get_db_connection()
        if not conn:
            return render_template('error.html', error="Failed to connect to database")

        # Execute query to get all sales data
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM salesm")
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Fetch all results
        results = cursor.fetchall()
        
        # Convert results to list of dicts
        sales_data = []
        for row in results:
            sales_data.append(dict(zip(columns, row)))
            
        # Close connection
        cursor.close()
        conn.close()
        
        return render_template('sales.html', columns=columns, sales_data=sales_data)
        
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/fetch-data', methods=['POST'])
def fetch_data():
    """API endpoint to fetch data from the database"""
    try:
        # Get query from request
        data = request.get_json()
        query = data.get('query', 'SELECT * FROM salesm LIMIT 100')

        # Connect to database
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Failed to connect to database"}), 500

        # Execute query
        cursor = conn.cursor()
        cursor.execute(query)

        # Get column names
        columns = [desc[0] for desc in cursor.description]

        # Fetch results
        results = cursor.fetchall()

        # Convert results to list of dicts
        formatted_results = []
        for row in results:
            formatted_results.append(dict(zip(columns, row)))

        # Close connection
        cursor.close()
        conn.close()

        return jsonify({
            "columns": columns,
            "data": formatted_results
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/tables')
def get_tables():
    """Get list of tables in the database"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Failed to connect to database"}), 500

        cursor = conn.cursor()
        # SQL Anywhere syntax for getting tables
        cursor.execute("SELECT table_name FROM sys.systable WHERE table_type = 'BASE'")

        tables = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return jsonify({"tables": tables})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Check if running on Render
    port = int(os.environ.get("PORT", 5000))
    # In production, don't use debug mode
    debug_mode = os.environ.get("RENDER", False) != "true"
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
