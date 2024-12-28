// Utility functions for form validation
const ValidationUtils = {
    displayError(inputElement, message) {
        // Remove any existing error message
        this.removeError(inputElement);
        
        // Create error element
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback d-block';
        errorDiv.textContent = message;
        
        // Insert after input element or after the role container for radio buttons
        const targetElement = inputElement.type === 'radio' ? 
            inputElement.closest('.role-container') : inputElement;
        targetElement.parentNode.insertBefore(errorDiv, targetElement.nextSibling);
        inputElement.classList.add('is-invalid');
    },

    removeError(inputElement) {
        const container = inputElement.type === 'radio' ? 
            inputElement.closest('.role-container') : inputElement.parentNode;
        const existingError = container.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }
        inputElement.classList.remove('is-invalid');
    },

    validatePassword(password) {
        const regex = /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
        return regex.test(password);
    },

    validateEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    },

    validateImage(file) {
        const allowedTypes = ['image/jpeg', 'image/png'];
        const maxSize = 2 * 1024 * 1024; // 2MB
        
        if (!allowedTypes.includes(file.type)) {
            return { valid: false, message: 'Please upload a valid JPEG or PNG image.' };
        }
        
        if (file.size > maxSize) {
            return { valid: false, message: 'Image size must be less than 2MB.' };
        }
        
        return { valid: true };
    }
};

// Registration Form Validation
class RegistrationForm {
    constructor() {
        this.form = document.getElementById('registrationForm');
        this.inputs = {
            fullName: document.getElementById('full_name'),
            email: document.getElementById('email'),
            password: document.getElementById('password'),
            confirmPassword: document.getElementById('confirm_password'),
            department: document.getElementById('department'),
            profilePicture: document.getElementById('profile_picture'),
            facultyRole: document.getElementById('faculty'),
            adminRole: document.getElementById('admin'),
            partnerRole: document.getElementById('partner')
        };
        
        // Add this line to debug
        console.log('Form inputs:', this.inputs);
        
        this.initializeValidation();
    }

    initializeValidation() {
        console.log('Initializing registration form validation');
        
        // Real-time validation
        this.inputs.fullName.addEventListener('input', () => this.validateFullName());
        this.inputs.password.addEventListener('input', () => this.validatePasswordStrength());
        this.inputs.confirmPassword.addEventListener('input', () => this.validatePasswordMatch());
        this.inputs.email.addEventListener('input', () => this.validateEmail());
        this.inputs.profilePicture.addEventListener('change', () => this.validateProfilePicture());
        this.inputs.department.addEventListener('change', () => this.validateDepartment());
        
        // Add role validation
        [this.inputs.facultyRole, this.inputs.adminRole, this.inputs.partnerRole].forEach(radio => {
            radio.addEventListener('change', () => this.validateRole());
        });
        
        // Form submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    validateFullName() {
        const fullName = this.inputs.fullName.value.trim();
        if (!fullName) {
            ValidationUtils.displayError(this.inputs.fullName, 'Full name is required.');
            return false;
        }
        if (fullName.length < 2) {
            ValidationUtils.displayError(this.inputs.fullName, 'Full name must be at least 2 characters long.');
            return false;
        }
        ValidationUtils.removeError(this.inputs.fullName);
        return true;
    }

    validatePasswordStrength() {
        const password = this.inputs.password.value;
        if (!ValidationUtils.validatePassword(password)) {
            ValidationUtils.displayError(
                this.inputs.password,
                'Password must include at least 8 characters, an uppercase letter, a lowercase letter, a number, and a special character.'
            );
            return false;
        }
        ValidationUtils.removeError(this.inputs.password);
        return true;
    }

    validatePasswordMatch() {
        if (this.inputs.password.value !== this.inputs.confirmPassword.value) {
            ValidationUtils.displayError(this.inputs.confirmPassword, 'Passwords do not match.');
            return false;
        }
        ValidationUtils.removeError(this.inputs.confirmPassword);
        return true;
    }

    validateEmail() {
        if (!ValidationUtils.validateEmail(this.inputs.email.value)) {
            ValidationUtils.displayError(this.inputs.email, 'Please enter a valid academic email address.');
            return false;
        }
        ValidationUtils.removeError(this.inputs.email);
        return true;
    }

    validateDepartment() {
        if (!this.inputs.department.value) {
            ValidationUtils.displayError(this.inputs.department, 'Please select your department.');
            return false;
        }
        ValidationUtils.removeError(this.inputs.department);
        return true;
    }

    validateRole() {
        const roleSelected = [
            this.inputs.facultyRole,
            this.inputs.adminRole,
            this.inputs.partnerRole
        ].some(radio => radio.checked);

        if (!roleSelected) {
            ValidationUtils.displayError(this.inputs.facultyRole, 'Please select your role.');
            return false;
        }
        ValidationUtils.removeError(this.inputs.facultyRole);
        return true;
    }

    validateProfilePicture() {
        const input = this.inputs.profilePicture;
        if (!input.files || !input.files[0]) {
            ValidationUtils.displayError(input, 'Profile picture is required.');
            return false;
        }

        const file = input.files[0];
        const maxSize = 2 * 1024 * 1024; // 2MB
        const allowedTypes = ['image/jpeg', 'image/png'];

        if (!allowedTypes.includes(file.type)) {
            ValidationUtils.displayError(input, 'Please upload a valid JPEG or PNG image.');
            return false;
        }

        if (file.size > maxSize) {
            ValidationUtils.displayError(input, 'Image size must be less than 2MB.');
            return false;
        }

        ValidationUtils.removeError(input);
        return true;
    }


    handleSubmit(e) {
        e.preventDefault();  // Add this line to prevent form submission
        console.log('Registration form submission attempted');
        
        let isValid = true;

        // Add detailed logging for each validation
    console.log('Password strength valid:', this.validatePasswordStrength());
    console.log('Password match valid:', this.validatePasswordMatch());
    console.log('Email valid:', this.validateEmail());
    console.log('Profile picture valid:', this.validateProfilePicture());
    console.log('Department valid:', this.validateDepartment());
    console.log('Role valid:', this.validateRole());
        
         // Validate all fields
         const validations = {
            fullName: this.validateFullName(),
            password: this.validatePasswordStrength(),
            passwordMatch: this.validatePasswordMatch(),
            email: this.validateEmail(),
            profilePicture: this.validateProfilePicture(),
            department: this.validateDepartment(),
            role: this.validateRole()
        };
        
        // Log all validation results
        Object.entries(validations).forEach(([field, valid]) => {
            console.log(`${field} valid:`, valid);
            isValid = isValid && valid;
        });

        if (!isValid) {
            console.log('Registration validation failed');
            return false;
        }

        console.log('Registration validation passed');
        this.form.submit();
    }
}

// Login Form Validation
class LoginForm {
    constructor() {
        this.form = document.getElementById('loginForm');
        this.inputs = {
            email: document.getElementById('id_email'),
            password: document.getElementById('id_password'),
            role: document.getElementById('id_role')
        };
        
        this.initializeValidation();
    }

    initializeValidation() {
        console.log('Initializing login form validation');
        
        // Real-time validation
        this.inputs.email.addEventListener('input', () => this.validateEmail());
        this.inputs.role.addEventListener('change', () => this.validateRole());
        
        // Form submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    validateEmail() {
        if (!ValidationUtils.validateEmail(this.inputs.email.value)) {
            ValidationUtils.displayError(this.inputs.email, 'Please enter a valid email address.');
            return false;
        }
        ValidationUtils.removeError(this.inputs.email);
        return true;
    }

    validateRole() {
        if (!this.inputs.role.value) {
            ValidationUtils.displayError(this.inputs.role, 'Please select your role.');
            return false;
        }
        ValidationUtils.removeError(this.inputs.role);
        return true;
    }

    validateRequiredFields() {
        let isValid = true;
        
        if (!this.inputs.password.value) {
            ValidationUtils.displayError(this.inputs.password, 'Password is required.');
            isValid = false;
        } else {
            ValidationUtils.removeError(this.inputs.password);
        }
        
        return isValid;
    }

    handleSubmit(e) {
        console.log('Login form submission attempted');
        
        let isValid = true;
        
        isValid = this.validateEmail() && isValid;
        isValid = this.validateRequiredFields() && isValid;
        isValid = this.validateRole() && isValid;
        
        if (!isValid) {
            e.preventDefault();
            console.log('Login validation failed');
        } else {
            console.log('Login validation passed');
        }
    }
}

// Initialize forms when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('registrationForm')) {
        new RegistrationForm();
    }
    if (document.getElementById('loginForm')) {
        new LoginForm();
    }
});
