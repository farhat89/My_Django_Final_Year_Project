// Utility functions for form validation
window.ValidationUtils = window.ValidationUtils || {
  displayError(inputElement, message) {
    // Remove any existing error message
    this.removeError(inputElement);

    // Create error element
    const errorDiv = document.createElement("div");
    errorDiv.className = "invalid-feedback d-block";
    errorDiv.textContent = message;

    // Insert after input element or after the role container for radio buttons
    const targetElement =
      inputElement.type === "radio"
        ? inputElement.closest(".role-container")
        : inputElement;
    targetElement.parentNode.insertBefore(errorDiv, targetElement.nextSibling);
    inputElement.classList.add("is-invalid");
  },

  removeError(inputElement) {
    const container =
      inputElement.type === "radio"
        ? inputElement.closest(".role-container")
        : inputElement.parentNode;
    const existingError = container.querySelector(".invalid-feedback");
    if (existingError) {
      existingError.remove();
    }
    inputElement.classList.remove("is-invalid");
  },

  validatePassword(password) {
    const regex =
      /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    return regex.test(password);
  },

  validateEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
  },

  validateImage(file) {
    const allowedTypes = ["image/jpeg", "image/png"];
    const maxSize = 2 * 1024 * 1024; // 2MB

    if (!allowedTypes.includes(file.type)) {
      return {
        valid: false,
        message: "Please upload a valid JPEG or PNG image.",
      };
    }

    if (file.size > maxSize) {
      return { valid: false, message: "Image size must be less than 2MB." };
    }

    return { valid: true };
  },
};

// Registration Form Validation
class RegistrationForm {
  constructor() {
    this.form = document.getElementById("registrationForm");
    this.inputs = {
      fullName: document.getElementById("full_name"),
      email: document.getElementById("email"),
      password: document.getElementById("password"),
      confirmPassword: document.getElementById("confirm_password"),
      department: document.getElementById("department"),
      profilePicture: document.getElementById("profile_picture"),
      facultyRole: document.getElementById("faculty"),
      adminRole: document.getElementById("admin"),
      partnerRole: document.getElementById("partner"),
    };

    // Add this line to debug
    console.log("Form inputs:", this.inputs);

    this.initializeValidation();
  }

  initializeValidation() {
    console.log("Initializing registration form validation");

    // Real-time validation
    this.inputs.fullName.addEventListener("input", () =>
      this.validateFullName()
    );
    this.inputs.password.addEventListener("input", () =>
      this.validatePasswordStrength()
    );
    this.inputs.confirmPassword.addEventListener("input", () =>
      this.validatePasswordMatch()
    );
    this.inputs.email.addEventListener("input", () => this.validateEmail());
    this.inputs.profilePicture.addEventListener("change", () =>
      this.validateProfilePicture()
    );
    this.inputs.department.addEventListener("change", () =>
      this.validateDepartment()
    );

    // Add role validation
    [
      this.inputs.facultyRole,
      this.inputs.adminRole,
      this.inputs.partnerRole,
    ].forEach((radio) => {
      radio.addEventListener("change", () => this.validateRole());
    });

    // Form submission
    this.form.addEventListener("submit", (e) => this.handleSubmit(e));
  }

  validateFullName() {
    const fullName = this.inputs.fullName.value.trim();
    if (!fullName) {
      ValidationUtils.displayError(
        this.inputs.fullName,
        "Full name is required."
      );
      return false;
    }
    if (fullName.length < 5) {
      ValidationUtils.displayError(
        this.inputs.fullName,
        "Full name must be at least 5 characters long."
      );
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
        "Password must include at least 8 characters, an uppercase letter, a lowercase letter, a number, and a special character."
      );
      return false;
    }
    ValidationUtils.removeError(this.inputs.password);
    return true;
  }

  validatePasswordMatch() {
    if (this.inputs.password.value !== this.inputs.confirmPassword.value) {
      ValidationUtils.displayError(
        this.inputs.confirmPassword,
        "Passwords do not match."
      );
      return false;
    }
    ValidationUtils.removeError(this.inputs.confirmPassword);
    return true;
  }

  validateEmail() {
    if (!ValidationUtils.validateEmail(this.inputs.email.value)) {
      ValidationUtils.displayError(
        this.inputs.email,
        "Please enter a valid email address."
      );
      return false;
    }
    if (this.inputs.email) {
      ValidationUtils.removeError(this.inputs.email);
    }
    return true;
  }

  validateDepartment() {
    if (!this.inputs.department.value) {
      ValidationUtils.displayError(
        this.inputs.department,
        "Please select your department."
      );
      return false;
    }
    ValidationUtils.removeError(this.inputs.department);
    return true;
  }

  validateRole() {
    const roleSelected = [
      this.inputs.facultyRole,
      this.inputs.adminRole,
      this.inputs.partnerRole,
    ].some((radio) => radio.checked);

    if (!roleSelected) {
      ValidationUtils.displayError(
        this.inputs.facultyRole,
        "Please select your role."
      );
      return false;
    }
    ValidationUtils.removeError(this.inputs.facultyRole);
    return true;
  }

  validateProfilePicture() {
    const input = this.inputs.profilePicture;
    if (!input.files || !input.files[0]) {
      ValidationUtils.displayError(input, "Profile picture is required.");
      return false;
    }

    const file = input.files[0];
    const validation = ValidationUtils.validateImage(file);

    if (!validation.valid) {
      ValidationUtils.displayError(input, validation.message);
      return false;
    }

    ValidationUtils.removeError(input);
    return true;
  }

 // Modified handleSubmit method in custom.js
handleSubmit(e) {
    e.preventDefault();
    console.log("Registration form submission attempted");

    // Validate all fields
    const validations = {
        fullName: this.validateFullName(),
        password: this.validatePasswordStrength(),
        passwordMatch: this.validatePasswordMatch(),
        email: this.validateEmail(),
        profilePicture: this.validateProfilePicture(),
        department: this.validateDepartment(),
        role: this.validateRole(),
    };

    let isValid = true;
    Object.entries(validations).forEach(([field, valid]) => {
        console.log(`${field} valid:`, valid);
        isValid = isValid && valid;
    });

    if (!isValid) {
        console.log("Registration validation failed");
        return false;
    }

    console.log("Registration validation passed");

    // Create FormData object
    const formData = new FormData(this.form);

    // Enhanced debug logging for form data
    console.log("=== Form Data Debug Log ===");
    for (let [key, value] of formData.entries()) {
        console.log(`${key}:`, value instanceof File ? `File: ${value.name}` : value);
    }
    console.log("=========================");

    // Get CSRF token from the form
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    try {
        // Submit form using fetch with correct headers
        fetch(this.form.action, {
            method: "POST",
            body: formData,  // Send FormData directly
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": csrfToken
                // Remove Content-Type header - browser will set it automatically with boundary for FormData
            },
            credentials: "same-origin",
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(JSON.stringify(data));
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Server response:', data);
            if (data.success) {
                window.location.href = data.redirect_url;
            } else {
                // Better error handling
                if (data.message) {
                    if (typeof data.message === 'object') {
                        Object.entries(data.message).forEach(([field, errors]) => {
                            const input = this.inputs[field];
                            if (input) {
                                ValidationUtils.displayError(input, 
                                    Array.isArray(errors) ? errors[0] : errors);
                            }
                        });
                    } else {
                        // Display general error message
                        alert(data.message);
                    }
                }
            }
        })
        .catch(error => {
            console.error('Submission error:', error);
            try {
                const errorData = JSON.parse(error.message);
                if (errorData.message) {
                    Object.entries(errorData.message).forEach(([field, errors]) => {
                        const input = this.inputs[field];
                        if (input) {
                            ValidationUtils.displayError(input, 
                                Array.isArray(errors) ? errors[0] : errors);
                        }
                    });
                }
            } catch (e) {
                alert('An error occurred during registration. Please try again.');
            }
        });
    } catch (error) {
        console.error('Try-catch submission error:', error);
    }
}
}

// Initialize forms when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  const registrationForm = document.getElementById("registrationForm");
  const loginForm = document.getElementById("loginForm");

  if (registrationForm && !registrationForm._initialized) {
    new RegistrationForm();
    registrationForm._initialized = true;
  }

  if (loginForm && !loginForm._initialized) {
    new LoginForm();
    loginForm._initialized = true;
  }
});