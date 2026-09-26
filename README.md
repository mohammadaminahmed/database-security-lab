# 🛡️ Database Security Lab: Vertical Privilege Escalation

## ⚠️ Disclaimer
**This project was created for educational and academic purposes only.** 
It is designed to demonstrate a specific web and database security vulnerability (Vertical Privilege Escalation) in a controlled, local environment. Do not use these concepts or codes to attack systems you do not own or have explicit permission to test.

## 📖 Project Overview
This repository contains a lightweight PHP/MySQL web application built to illustrate the **Vertical Privilege Escalation** vulnerability. It highlights the intersection between Application Security and Database Security by showing how improper access controls in the application layer can expose sensitive database records to unauthorized users.

## 🐛 The Vulnerability (How it Works)
Vertical Privilege Escalation occurs when a system verifies if a user is authenticated (logged in) but fails to verify if the user is authorized (has the correct Role/Privileges) to access a specific resource.

In this lab:
1. The application checks the `$_SESSION['logged_in']` state.
2. It forgets to validate the database `Role` column (e.g., User vs. Admin).
3. A low-privileged user can manipulate the URL to directly access the database administration dashboard (`admin_vuln.php`).

## ⚙️ Lab Setup & Installation
To run this lab locally, you need a local web server with PHP and MySQL (like [XAMPP](https://www.apachefriends.org/)).

1. Clone this repository into your local server directory (e.g., `C:\xampp\htdocs\vulnlab`).
2. Start **Apache** and **MySQL** from your XAMPP Control Panel.
3. Open your browser and navigate to `http://localhost/vulnlab/seed.php`. This script will automatically create the `vulnlab_db` database and populate it with dummy accounts:
   * **Admin Account:** `admin` / `admin123`
   * **Standard User:** `student` / `student123`

## 🎯 Proof of Concept (Exploitation)
1. Go to `http://localhost/vulnlab/login.php`.
2. Log in using the standard user credentials (`student`).
3. You will be redirected to `profile.php`.
4. **The Attack:** In the browser's URL bar, change `profile.php` to `admin_vuln.php` and hit Enter.
5. **Result:** You now have full access to the Admin Dashboard without having admin privileges in the database.

## 🔐 The Fix (Remediation)
To patch this vulnerability, **Role-Based Access Control (RBAC)** must be implemented. The system must query the user's role from the session or database before granting access.

Check `admin_fixed.php` for the secure implementation:
```php
session_start();

// 1. Authentication Check
if (!isset($_SESSION['logged_in']) \vert{}\vert{}$_SESSION['logged_in'] !== true) {
    header("Location: login.php");
    exit;
}

// 2. Authorization Check (The Fix)
if ($_SESSION['role'] !== 'admin') {
    die("HTTP 403 Forbidden: You do not have permission to access this page.");
}



👨‍💻 Contributors
[ Mohammed amin ahmed Al-Huthifi]
