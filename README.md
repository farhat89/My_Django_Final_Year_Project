# Faculty Collaboration Platform

An intranet-based file-sharing and collaboration platform tailored for faculty members. This platform provides a secure and efficient way for faculty members to share files, manage users, and collaborate on academic projects.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [License](#license)
- [Contributing](#contributing)
- [Contact](#contact)

## Overview

The Faculty Collaboration Platform is designed to enhance academic collaboration by providing features such as file sharing, user management, and real-time collaboration tools. It is role-specific and tailored for Admins, Faculty members, and External Partners, ensuring each user has access to relevant features.

### Target Audience

- **Admin**: Manage users, system configurations, and monitor activities.
- **Faculty Members**: Share and manage files, collaborate with peers, and engage in discussions.
- **External Partners**: Access shared files and collaborate on specific projects.

---

## Features

1. **User Registration**:
   - New users can register by providing basic details such as email, password, and role (Faculty, Admin, or External Partner).
   - Email validation and error handling.

2. **User Authentication**:
   - Secure login and logout functionality.
   - Role-based access (Admin, Faculty, External Partner).

3. **File Sharing**:
   - Upload, share, and manage files with metadata.
   - Visibility settings for shared files.

4. **Collaboration Tools**:
   - Real-time chat for discussions.
   - Shared workspaces for active collaborations.

5. **Notifications**:
   - Receive updates for file uploads, collaborations, and system changes.

6. **User Management (Admin)**:
   - Add, edit, and deactivate users.
   - View activity logs.

7. **Responsive Design**:
   - Optimized for desktops, tablets, and mobile devices.

---

## Technologies Used

- **Frontend**: HTML, Bootstrap, JavaScript, Font Awesome
- **Backend**: Django
- **Database**: MySQL/PostgreSQL (configurable)
- **Other**: Django Channels (for real-time features)

---

## Setup Instructions

### Prerequisites
- Python 3.9 or higher
- Django 4.x or higher
- MySQL/PostgreSQL
- Node.js (optional, for managing frontend dependencies)

### Steps to Run the Project

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/faculty-collaboration-platform.git
   cd faculty-collaboration-platform

2. Set Up a Virtual Environment:
    1.     python -m venv venv #create virtual env
    2.     source venv/bin/activate  //to activate on Mac Os.     venv\Scripts\activate   //to activate On Windows.
       
4. Install Dependencies:
   
        pip install -r requirements.txt
   
6. Configure the Database:
   
        Open settings.py and update the DATABASES setting with your database credentials.
   
8. Apply Migrations:
   
       1. python manage.py makemigrations
       2. python manage.py migrate
   
10. Collect Static Files:
    
        python manage.py collectstatic
    
12. Run the Server:
    
        python manage.py runserver
    
14. Access the Platform: Open your browser and navigate to http://127.0.0.1:8000.


Usage

User Registration

    New users can register by visiting the Registration Page (/auth/register/).
    
Registration requires providing:

    Name
    Email address
    Password
    User role (Admin, Faculty, or External Partner)
    
Login

    Once registered, users can log in using their credentials.
    
File Sharing

    Faculty members can upload files and set visibility permissions.
    Admins can monitor file-sharing activities.
    
Collaboration

    Use the real-time chat and discussion panels to collaborate on projects.
    
User Management

    Admins can add or deactivate users, and view logs for monitoring activities.

License

    This project is licensed under the MIT License. See the LICENSE file for details.

Contributing

    Contributions are welcome! To contribute:

Fork the repository.

    Create a feature branch (git checkout -b feature-name).
    Commit your changes (git commit -m 'Add new feature').
    Push to the branch (git push origin feature-name).
    Open a pull request.
    
Contact

    For questions or support, please contact:
    Email: farhatnasfat2020@gmail.com
    Author: Idris Nasir Ibrahim (@farhat89)





       
