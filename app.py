from flask import Flask, request, jsonify, render_template_string
from flask_mysqldb import MySQL

app = Flask(__name__)

# 1. Configure MySQL Database Connection Parameters
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'crud_db'

mysql = MySQL(app)

# Helper function to fetch the complete formatted user list
def get_all_users_list(cursor):
    cursor.execute("SELECT user_id, user_name, user_email FROM tbl_user")
    rows = cursor.fetchall()
    
    user_list = []
    for row in rows:
        user_list.append({
            "user_id": row[0],
            "user_name": row[1],
            "user_email": row[2]
        })
    return user_list

# 2. Modern Bootstrap 5 Single Page Application Layout
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Customer Registry Dashboard</title>
    <!-- Bootstrap 5 CSS CDN (Fixed Absolute Paths) -->
    <link href="jsdelivr.net" rel="stylesheet">
    <!-- Bootstrap Icons CDN -->
    <link href="jsdelivr.net" rel="stylesheet">
    <style>
        body { background-color: #f4f6f9; font-family: 'Segoe UI', system-ui, sans-serif; }
        .customer-card { border: none; border-radius: 12px; transition: transform 0.2s, box-shadow 0.2s; background: white; }
        .customer-card:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.08)!important; }
        .avatar-circle { width: 48px; height: 48px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; }
        .form-control { border-radius: 8px; }
        .btn { border-radius: 8px; }
    </style>
</head>
<body>

    <div class="container py-5">
        <!-- Header -->
        <header class="d-flex flex-column flex-md-row justify-content-between align-items-md-center pb-3 mb-5 border-bottom">
            <div>
                <h1 class="fw-bold text-dark mb-1"><i class="bi bi-people-fill text-primary"></i> Customer Directory</h1>
                <p class="text-muted mb-0">Unified Single Page Application powered by Flask & Bootstrap 5.</p>
            </div>
            <div class="mt-2 mt-md-0">
                <button onclick="fetchCustomers()" class="btn btn-outline-primary btn-sm fw-semibold">
                    <i class="bi bi-arrow-clockwise"></i> Sync Database
                </button>
            </div>
        </header>

        <!-- Status Alerts -->
        <div id="statusAlert" class="alert d-none mb-4" role="alert"></div>

        <div class="row g-4">
            <!-- Left Side Input Actions Column -->
            <div class="col-12 col-lg-4">
                <div class="card shadow-sm border p-4 bg-white sticky-top" style="top: 24px; z-index: 10;">
                    <h5 class="fw-bold text-dark mb-4"><i class="bi bi-person-plus-fill text-success"></i> Register New Customer</h5>
                    
                    <form id="customerForm">
                        <div class="mb-3">
                            <label class="form-label text-muted fw-semibold small text-uppercase">Full Name</label>
                            <input type="text" id="custName" required placeholder="e.g. Pankaj Kumar" class="form-control form-control-lg fs-6 shadow-none">
                        </div>
                        <div class="mb-4">
                            <label class="form-label text-muted fw-semibold small text-uppercase">Email Address</label>
                            <input type="email" id="custEmail" required placeholder="e.g. pankaj@example.com" class="form-control form-control-lg fs-6 shadow-none">
                        </div>
                        <button type="submit" class="btn btn-primary w-100 fw-bold py-2.5 shadow-sm">
                            <i class="bi bi-check-circle-fill me-1"></i> Add Customer
                        </button>
                    </form>
                </div>
            </div>

            <!-- Right Side Customer Cards Display Area -->
            <div class="col-12 col-lg-8">
                <h5 class="fw-bold text-dark mb-4"><i class="bi bi-grid-fill text-primary"></i> Active Customer Profiles</h5>
                
                <!-- Dynamic Card Grid Container -->
                <div id="cardsContainer" class="row row-cols-1 row-cols-md-2 g-3">
                    <!-- Cards mount here dynamically -->
                </div>
            </div>
        </div>
    </div>

    <!-- Asynchronous Client Core Engine -->
    <script>
        // Points natively to the same domain host environment context
        const API_BASE_URL = window.location.origin;

        const dashboardHeaders = { 
            'X-Requested-From': 'Dashboard',
            'Accept': 'application/json',
            'Bypass-Tunnel-Reminder': 'true'
        };

        function displayNotification(message, isSuccess = true) {
            const alertBox = document.getElementById('statusAlert');
            alertBox.className = `alert shadow-sm border mb-4 d-block ${isSuccess ? 'alert-success border-success-subtle' : 'alert-danger border-danger-subtle'}`;
            alertBox.innerHTML = `<i class="bi ${isSuccess ? 'bi-check-circle' : 'bi-exclamation-triangle'}-fill me-2"></i> ${message}`;
            setTimeout(() => { alertBox.className = 'alert d-none'; }, 4000);
        }

        // 1. FETCH ASYNC: Read records and render them as cards on the same page
        async function fetchCustomers() {
            try {
                const response = await fetch(`${API_BASE_URL}/users`, { headers: dashboardHeaders });
                const data = await response.json();
                const container = document.getElementById('cardsContainer');
                container.innerHTML = '';

                // Filter out trailing layout metadata strings
                const customers = data.filter(item => item.user_id !== undefined);

                if (customers.length === 0) {
                    container.innerHTML = `
                        <div class="col-12 w-100 text-center py-5 bg-white border rounded-3 text-muted italic">
                            <i class="bi bi-journal-x display-6 d-block mb-2 text-muted"></i> No customers registered yet.
                        </div>`;
                    return;
                }

                customers.forEach(customer => {
                    const initialToken = customer.user_name ? customer.user_name.charAt(0).toUpperCase() : '?';
                    container.innerHTML += `
                        <div class="col">
                            <div class="card customer-card h-100 shadow-sm border p-3">
                                <div class="d-flex align-items-center justify-content-between mb-2">
                                    <div class="avatar-circle bg-primary-subtle text-primary">${initialToken}</div>
                                    <span class="text-muted font-monospace small fw-bold">#ID-${customer.user_id}</span>
                                </div>
                                <h6 class="fw-bold text-dark mb-1 text-truncate">${customer.user_name}</h6>
                                <p class="text-secondary small mb-3 text-truncate"><i class="bi bi-envelope me-1"></i>${customer.user_email}</p>
                                <div class="border-top pt-2 text-end">
                                    <button onclick="deleteCustomer('${customer.user_name}')" class="btn btn-sm btn-link text-danger text-decoration-none p-0 fw-semibold">
                                        <i class="bi bi-trash3"></i> Remove Profile
                                    </button>
                                </div>
                            </div>
                        </div>`;
                });
            } catch (err) {
                displayNotification("Connection breakdown. Could not communicate with database infrastructure.", false);
            }
        }

        // 2. POST ASYNC: Add a new entry on the same page via AJAX
        document.getElementById('customerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const name = document.getElementById('custName').value.trim();
            const email = document.getElementById('custEmail').value.trim();

            try {
                const res = await fetch(`${API_BASE_URL}/userc?name=${encodeURIComponent(name)}&email=${encodeURIComponent(email)}`, { headers: dashboardHeaders });
                if (res.ok) {
                    displayNotification(`Customer "${name}" has been registered successfully.`);
                    document.getElementById('customerForm').reset();
                    fetchCustomers();
                } else {
                    const errorResponse = await res.json();
                    displayNotification(errorResponse.error || "Failed to register customer.", false);
                }
            } catch (err) {
                displayNotification("Network operational timeout during processing.", false);
            }
        });

        // 3. DELETE ASYNC: Wipe a record on the same page via AJAX
        async function deleteCustomer(name) {
            if (!confirm(`Are you sure you want to drop profile: "${name}"?`)) return;

            try {
                const res = await fetch(`${API_BASE_URL}/userd?name=${encodeURIComponent(name)}`, { headers: dashboardHeaders });
                if (res.ok) {
                    displayNotification(`Customer "${name}" dropped from database records.`);
                    fetchCustomers();
                } else {
                    displayNotification(`Could not drop profile. "${name}" is not active.`, false);
                }
            } catch (err) {
                displayNotification("Network drop request transmission error.", false);
            }
        }

        window.onload = fetchCustomers;
    </script>
    
    <!-- Bootstrap Bundle JS CDN -->
    <script src="jsdelivr.net"></script>
</body>
</html>
"""

# 3. ROUTE: HOME GATEWAY SERVING GRAPHICAL GUI
@app.route('/', methods=['GET'])
def home_dashboard():
    return render_template_string(DASHBOARD_HTML)

# 4. ROUTE: LIST ALL USERS FROM DATABASE
@app.route('/users', methods=['GET'])
def list_all_users():
    try:
        cur = mysql.connection.cursor()
        user_list = get_all_users_list(cur)
        cur.close()
        
        # Append target operational instruction line to the end of the JSON array
        user_list.append({
            "instruction": "To add a user, go to /userc?name=abc&email=abc.com. To delete a user, go to /userd?name=abc"
        })
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 5. ROUTE: ADD USER VIA URL QUERY PARAMETERS
@app.route('/userc', methods=['GET'])
def add_user_via_url():
    name = request.args.get('name')
    email = request.args.get('email')

    if not name or not email:
        return jsonify({
            "error": "Missing query parameters.",
            "instruction": "Please build your URL target exactly like this: /userc?name=abc&email=abc.com"
        }), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tbl_user(user_name, user_email) VALUES (%s, %s)", (name, email))
        mysql.connection.commit()
        
        user_list = get_all_users_list(cur)
        cur.close()
        
        user_list.append({
            "instruction": "User added successfully! Modify your parameters to add more users: /userc?name=abc&email=abc.com"
        })
        return jsonify(user_list), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 6. ROUTE: DELETE USER BY URL QUERY PARAMETER (BY NAME)
@app.route('/userd', methods=['GET'])
def delete_user_via_url():
    name = request.args.get('name')

    if not name:
        return jsonify({
            "error": "Missing target query parameter.",
            "instruction": "Please pass the user name to remove like this: /userd?name=abc"
        }), 400

    try:
        cur = mysql.connection.cursor()
        
        # Check if the user profile exists before attempting drop
        cur.execute("SELECT user_id FROM tbl_user WHERE user_name = %s", (name,))
        if not cur.fetchone():
            user_list = get_all_users_list(cur)
            cur.close()
            user_list.append({
                "error": f"User '{name}' not found.",
                "instruction": "Verify spelling or review active profiles at /users"
            })
            return jsonify(user_list), 404
            
        # Execute query statement removal operation mapping
        cur.execute("DELETE FROM tbl_user WHERE user_name = %s", (name,))
        mysql.connection.commit()
        
        # Pull fresh repository layout records state mapping
        user_list = get_all_users_list(cur)
        cur.close()
        
        user_list.append({
            "instruction": f"User '{name}' deleted successfully! View changes above or use /userc to append values."
        })
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('APP_PORT', 5000))
    log.info(f"Starting Flask on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port)
