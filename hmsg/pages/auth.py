"""Authentication page components."""

import reflex as rx
from ..services.auth_service import authenticate_user, create_user
from ..services.database import ProfileType, User, get_session


class AuthState(rx.State):
    """Authentication state."""
    
    # Form fields
    username: str = ""
    password: str = ""
    profile: str = "patient"  # Default profile
    
    # Authentication status
    is_authenticated: bool = False
    current_user: str = ""
    current_profile: str = ""
    current_user_id: int = 0
    
    # UI state
    show_login: bool = True
    error_message: str = ""
    success_message: str = ""

    def set_username(self, username: str):
        """Set username."""
        self.username = username

    def set_password(self, password: str):
        """Set password."""
        self.password = password
    
    def handle_key_down(self, key: str):
        """Handle key down events for Enter to login."""
        if key == "Enter":
            return self.login()
        
    def set_profile(self, profile: str):
        """Set profile type for registration."""
        self.profile = profile

    def login(self):
        """Handle user login."""
        if not self.username or not self.password:
            self.error_message = "Please enter both username and password"
            return
            
        # Basic validation
        if len(self.username.strip()) < 3:
            self.error_message = "Username must be at least 3 characters"
            return
            
        if len(self.password) < 6:
            self.error_message = "Password must be at least 6 characters"
            return
            
        db = get_session()
        try:
            user = authenticate_user(db, self.username.strip(), self.password)
            if user:
                self.is_authenticated = True
                self.current_user = user.name
                self.current_profile = user.profile.value
                self.current_user_id = user.id
                self.error_message = ""
                self.username = ""
                self.password = ""
                
                # Redirect based on profile
                if user.profile.value == "doc":
                    return rx.redirect("/dashboard")
                else:
                    return rx.redirect("/patient")
            else:
                self.error_message = "Invalid username or password"
        finally:
            db.close()

    def register(self):
        """Handle user registration."""
        if not self.username or not self.password:
            self.error_message = "Please enter both username and password"
            return
            
        db = get_session()
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(User.username == self.username).first()
            if existing_user:
                self.error_message = "Username already exists"
                return
            
            # Create new user
            profile_type = ProfileType.DOC if self.profile == "doc" else ProfileType.PATIENT
            create_user(db=db, username=self.username, name=self.username, profile=profile_type, password=self.password)
            self.success_message = f"Account created successfully! You can now login."
            self.error_message = ""
            self.username = ""
            self.password = ""
        except Exception as e:
            self.error_message = f"Registration failed: {str(e)}"
        finally:
            db.close()

    def logout(self):
        """Handle user logout."""
        self.is_authenticated = False
        self.current_user = ""
        self.current_profile = ""
        self.current_user_id = 0
        self.error_message = ""
        self.success_message = ""
        return rx.redirect("/")

    def toggle_form(self):
        """Toggle between login and register forms."""
        self.show_login = not self.show_login
        self.error_message = ""
        self.success_message = ""
        self.username = ""
        self.password = ""


def login_form() -> rx.Component:
    """Login form component."""
    return rx.vstack(
        rx.heading("Login", size="7"),
        rx.input(
            placeholder="Username",
            value=AuthState.username,
            on_change=AuthState.set_username,
            on_key_down=AuthState.handle_key_down,
            width="100%",
        ),
        rx.input(
            placeholder="Password",
            type="password",
            value=AuthState.password,
            on_change=AuthState.set_password,
            on_key_down=AuthState.handle_key_down,
            width="100%",
        ),
        rx.button(
            "Login",
            on_click=AuthState.login,
            width="100%",
            color_scheme="blue",
        ),
        rx.cond(
            AuthState.error_message != "",
            rx.text(AuthState.error_message, color="red"),
        ),
        rx.cond(
            AuthState.success_message != "",
            rx.text(AuthState.success_message, color="green"),
        ),
        rx.button(
            "Don't have an account? Register",
            on_click=lambda: rx.redirect("/register"),
            variant="ghost",
            size="2",
        ),
        spacing="4",
        width="400px",
    )


def register_form() -> rx.Component:
    """Registration form component."""
    return rx.vstack(
        rx.heading("Register", size="7"),
        rx.input(
            placeholder="Username",
            value=AuthState.username,
            on_change=AuthState.set_username,
            width="100%",
        ),
        rx.input(
            placeholder="Password",
            type="password",
            value=AuthState.password,
            on_change=AuthState.set_password,
            width="100%",
        ),
        rx.select(
            ["patient", "doc"],
            placeholder="Select Profile Type",
            value=AuthState.profile,
            on_change=AuthState.set_profile,
            width="100%",
        ),
        rx.button(
            "Register",
            on_click=AuthState.register,
            width="100%",
            color_scheme="green",
        ),
        rx.cond(
            AuthState.error_message != "",
            rx.text(AuthState.error_message, color="red"),
        ),
        rx.cond(
            AuthState.success_message != "",
            rx.text(AuthState.success_message, color="green"),
        ),
        rx.button(
            "Already have an account? Login",
            on_click=AuthState.toggle_form,
            variant="ghost",
            size="2",
        ),
        spacing="4",
        width="400px",
    )


def auth_page() -> rx.Component:
    """Authentication page."""
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.cond(
                AuthState.show_login,
                login_form(),
                register_form(),
            ),
            spacing="6",
            justify="center",
            min_height="85vh",
        ),
        padding="8",
        max_width="600px",
        margin="0 auto",
    ) 