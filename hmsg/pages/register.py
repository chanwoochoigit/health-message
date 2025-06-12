"""Registration page for new users."""

import reflex as rx
from ..services.auth_service import create_user
from ..services.database import SessionLocal, ProfileType, User


class RegisterState(rx.State):
    """Registration state."""
    
    # Form fields
    username: str = ""
    password: str = ""
    confirm_password: str = ""
    full_name: str = ""
    email: str = ""
    profile: str = "patient"  # Default profile
    
    # UI state
    error_message: str = ""
    success_message: str = ""
    is_loading: bool = False

    def set_username(self, username: str):
        """Set username."""
        self.username = username.strip()

    def set_password(self, password: str):
        """Set password."""
        self.password = password
        
    def set_confirm_password(self, confirm_password: str):
        """Set confirm password."""
        self.confirm_password = confirm_password

    def set_full_name(self, full_name: str):
        """Set full name."""
        self.full_name = full_name.strip()
        
    def set_email(self, email: str):
        """Set email."""
        self.email = email.strip()

    def set_profile(self, profile: str):
        """Set profile type."""
        self.profile = profile

    def validate_form(self) -> bool:
        """Validate registration form."""
        if not self.username:
            self.error_message = "Username is required"
            return False
            
        if len(self.username) < 3:
            self.error_message = "Username must be at least 3 characters"
            return False
            
        if not self.full_name:
            self.error_message = "Full name is required"
            return False
            
        if not self.password:
            self.error_message = "Password is required"
            return False
            
        if len(self.password) < 6:
            self.error_message = "Password must be at least 6 characters"
            return False
            
        if self.password != self.confirm_password:
            self.error_message = "Passwords do not match"
            return False
            
        if self.email and "@" not in self.email:
            self.error_message = "Please enter a valid email address"
            return False
            
        return True

    def register(self):
        """Handle user registration."""
        if not self.validate_form():
            return
            
        self.is_loading = True
        self.error_message = ""
        
        db = SessionLocal()
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(User.username == self.username).first()
            if existing_user:
                self.error_message = "Username already exists"
                return
            
            # Create new user
            profile_type = ProfileType.DOC if self.profile == "doc" else ProfileType.PATIENT
            create_user(
                db=db, 
                username=self.username, 
                name=self.full_name, 
                profile=profile_type, 
                password=self.password
            )
            
            self.success_message = f"Account created successfully! You can now login."
            self.error_message = ""
            
            # Clear form
            self.username = ""
            self.password = ""
            self.confirm_password = ""
            self.full_name = ""
            self.email = ""
            
        except Exception as e:
            self.error_message = f"Registration failed: {str(e)}"
        finally:
            self.is_loading = False
            db.close()

    def go_to_login(self):
        """Redirect to login page."""
        return rx.redirect("/")


def register_page() -> rx.Component:
    """Registration page."""
    return rx.container(
        rx.vstack(
            # Header
            rx.vstack(
                rx.heading("Create Account", size="8", weight="bold", color="#111827"),
                rx.text("Join our health monitoring platform", color="#6B7280", size="4"),
                spacing="2",
                align="center",
            ),
            
            # Registration form
            rx.vstack(
                # Full Name
                rx.vstack(
                    rx.text("Full Name", size="3", weight="medium", color="#374151"),
                    rx.input(
                        placeholder="Enter your full name",
                        value=RegisterState.full_name,
                        on_change=RegisterState.set_full_name,
                        width="100%",
                        size="3",
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                
                # Username
                rx.vstack(
                    rx.text("Username", size="3", weight="medium", color="#374151"),
                    rx.input(
                        placeholder="Choose a username",
                        value=RegisterState.username,
                        on_change=RegisterState.set_username,
                        width="100%",
                        size="3",
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                
                # Email (optional)
                rx.vstack(
                    rx.text("Email (Optional)", size="3", weight="medium", color="#374151"),
                    rx.input(
                        placeholder="Enter your email",
                        value=RegisterState.email,
                        on_change=RegisterState.set_email,
                        width="100%",
                        size="3",
                        type="email",
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                
                # Profile Type
                rx.vstack(
                    rx.text("Account Type", size="3", weight="medium", color="#374151"),
                    rx.select(
                        ["patient", "doc"],
                        placeholder="Select account type",
                        value=RegisterState.profile,
                        on_change=RegisterState.set_profile,
                        width="100%",
                        size="3",
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                
                # Password
                rx.vstack(
                    rx.text("Password", size="3", weight="medium", color="#374151"),
                    rx.input(
                        placeholder="Create a password",
                        type="password",
                        value=RegisterState.password,
                        on_change=RegisterState.set_password,
                        width="100%",
                        size="3",
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                
                # Confirm Password
                rx.vstack(
                    rx.text("Confirm Password", size="3", weight="medium", color="#374151"),
                    rx.input(
                        placeholder="Confirm your password",
                        type="password",
                        value=RegisterState.confirm_password,
                        on_change=RegisterState.set_confirm_password,
                        width="100%",
                        size="3",
                    ),
                    spacing="1",
                    align="start",
                    width="100%",
                ),
                
                spacing="4",
                width="100%",
            ),
            
            # Submit button
            rx.button(
                rx.cond(
                    RegisterState.is_loading,
                    rx.hstack(
                        rx.spinner(size="1"),
                        rx.text("Creating Account..."),
                        spacing="2",
                        align="center",
                    ),
                    rx.text("Create Account"),
                ),
                on_click=RegisterState.register,
                width="100%",
                size="3",
                bg="#181C62",
                color="white",
                _hover={"bg": "#141A55"},
                disabled=RegisterState.is_loading,
            ),
            
            # Error/Success messages
            rx.cond(
                RegisterState.error_message != "",
                rx.text(RegisterState.error_message, color="red", size="3"),
            ),
            rx.cond(
                RegisterState.success_message != "",
                rx.text(RegisterState.success_message, color="green", size="3"),
            ),
            
            # Login link
            rx.hstack(
                rx.text("Already have an account?", color="#6B7280", size="3"),
                rx.button(
                    "Sign In",
                    on_click=RegisterState.go_to_login,
                    variant="ghost",
                    size="3",
                    color="#181C62",
                ),
                spacing="2",
                justify="center",
            ),
            
            spacing="6",
            width="100%",
            max_width="400px",
        ),
        
        padding="8",
        max_width="500px",
        margin="0 auto",
        min_height="100vh",
        display="flex",
        align_items="center",
        justify_content="center",
    ) 