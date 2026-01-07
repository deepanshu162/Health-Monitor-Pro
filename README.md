
<body>

<h1>🩺 Health Monitor Pro</h1>

<p>
<strong>Health Monitor Pro</strong> is a <strong>Python-based desktop application</strong>
built using <strong>Tkinter</strong> that helps users
<strong>track, analyze, and predict health metrics</strong> such as
<strong>Blood Pressure</strong> and <strong>Blood Sugar</strong>.
</p>

<p>
The system includes <strong>secure authentication</strong>,
<strong>data visualization</strong>, <strong>PDF report generation</strong>,
and <strong>machine-learning-based predictions</strong>.
</p>

<h2>✨ Features</h2>

<h3>🔐 User Authentication</h3>
<ul>
    <li>Secure Login & Registration</li>
    <li>SHA-256 password hashing</li>
    <li>User profile management (age, gender, diabetes type)</li>
</ul>

<h3>❤️ Blood Pressure Monitoring</h3>
<ul>
    <li>Record systolic and diastolic readings</li>
    <li>View complete history</li>
    <li>Generate PDF reports</li>
    <li>Trend visualization</li>
    <li>7-day prediction using Linear Regression</li>
</ul>

<h3>🍬 Blood Sugar Monitoring</h3>
<ul>
    <li>Track glucose levels with meal context</li>
    <li>Diabetes-aware interpretation</li>
    <li>Trend visualization</li>
    <li>PDF report generation</li>
    <li>7-day glucose prediction</li>
</ul>

<h3>📊 Health Summary Dashboard</h3>
<ul>
    <li>Latest BP and BS readings</li>
    <li>Status classification (Normal, Elevated, Hypertension, etc.)</li>
    <li>Graphical trends</li>
</ul>

<h3>🤖 Prediction Engine</h3>
<ul>
    <li>Uses Scikit-Learn Linear Regression</li>
    <li>Graph-based prediction output</li>
    <li>Model evaluation metrics support</li>
</ul>

<h2>🛠️ Tech Stack</h2>

<table>
    <tr>
        <th>Category</th>
        <th>Technology</th>
    </tr>
    <tr>
        <td>Programming Language</td>
        <td>Python 3</td>
    </tr>
    <tr>
        <td>GUI</td>
        <td>Tkinter (ttk)</td>
    </tr>
    <tr>
        <td>Database</td>
        <td>SQLite</td>
    </tr>
    <tr>
        <td>Visualization</td>
        <td>Matplotlib</td>
    </tr>
    <tr>
        <td>Data Handling</td>
        <td>Pandas</td>
    </tr>
    <tr>
        <td>Machine Learning</td>
        <td>Scikit-Learn</td>
    </tr>
    <tr>
        <td>Reports</td>
        <td>FPDF</td>
    </tr>
    <tr>
        <td>Images</td>
        <td>Pillow (PIL)</td>
    </tr>
</table>

<h2>📂 Project Structure</h2>

<pre>
Health-Monitor-Pro/
│
├── main.py
├── auth_module.py
├── bp_module.py
├── bs_module.py
├── predict_module.py
├── generate_test_data.py
├── health_monitor.db
│
├── assets/
│   ├── health_logo.png
│   ├── auth_bg.jpg
│   ├── bp_icon.png
│   └── bs_icon.png
│
└── README.md
</pre>

<h2>⚙️ Installation & Setup</h2>

<h3>1️⃣ Clone the Repository</h3>
<pre>
git clone https://github.com/your-username/health-monitor-pro.git
cd health-monitor-pro
</pre>

<h3>2️⃣ Install Required Libraries</h3>
<pre>
pip install pandas matplotlib scikit-learn pillow fpdf
</pre>

<p><em>Note: Tkinter is included by default with Python.</em></p>

<h3>3️⃣ (Optional) Generate Sample Data</h3>
<pre>
python generate_test_data.py
</pre>

<h2>🧪 Sample Login Credentials</h2>

<p>
The following <strong>sample user accounts</strong> are provided for testing and demonstration purposes.
These accounts are automatically created when running the sample data generator.
</p>

<table>
    <tr>
        <th>Username</th>
        <th>Password</th>
        <th>Diabetes Type</th>
        <th>Age</th>
        <th>Gender</th>
    </tr>
    <tr>
        <td>john_doe</td>
        <td>password123</td>
        <td>Type 2 Diabetes</td>
        <td>45</td>
        <td>Male</td>
    </tr>
    <tr>
        <td>jane_smith</td>
        <td>securepass</td>
        <td>Type 1 Diabetes</td>
        <td>32</td>
        <td>Female</td>
    </tr>
    <tr>
        <td>mike_johnson</td>
        <td>test1234</td>
        <td>Prediabetes</td>
        <td>58</td>
        <td>Male</td>
    </tr>
    <tr>
        <td>sarah_williams</td>
        <td>health123</td>
        <td>Gestational Diabetes</td>
        <td>29</td>
        <td>Female</td>
    </tr>
    <tr>
        <td>david_brown</td>
        <td>demo123</td>
        <td>No Diabetes</td>
        <td>50</td>
        <td>Male</td>
    </tr>
</table>

<p>
<strong>Note:</strong> These credentials are for <em>testing and academic demonstration only</em>.
Do not use them in a production environment.
</p>


<h3>4️⃣ Run the Application</h3>
<pre>
python main.py
</pre>

<h2>📈 Prediction Logic</h2>
<ul>
    <li>Uses Linear Regression</li>
    <li>Requires at least 3 readings</li>
    <li>Predicts future health trends</li>
    <li>Provides table and graph views</li>
</ul>

<h2>📄 Reports</h2>
<ul>
    <li>Auto-generated PDF reports</li>
    <li>Summary statistics</li>
    <li>Color-coded health indicators</li>
    <li>Recent readings table</li>
</ul>

<h2>🔒 Security</h2>
<ul>
    <li>SHA-256 password hashing</li>
    <li>User-specific data access</li>
    <li>SQLite relational integrity</li>
</ul>

<h2>🚀 Future Enhancements</h2>
<ul>
    <li>Cloud backup and sync</li>
    <li>Mobile & Web versions</li>
    <li>Advanced ML models (LSTM)</li>
    <li>Doctor sharing and alerts</li>
</ul>

<footer>
    <p><strong>Author:</strong> Deepanshu Gupta</p>
    <p>Computer Science Student | Python | Data Analysis | Desktop Applications</p>
    
</footer>

</body>
</html>
