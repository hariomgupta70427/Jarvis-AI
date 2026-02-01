from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy, QAbstractScrollArea, QScrollArea, QGraphicsDropShadowEffect, QSpacerItem
from PyQt5.QtGui import QIcon, QPainter, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat, QTextOption, QMovie, QLinearGradient, QBrush, QPen, QFontDatabase
from PyQt5.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, QRect, QPoint
from dotenv import dotenv_values
import os
import sys

try:
    env_vars = dotenv_values(".env")
    Assistantname = env_vars.get("Assistantname", "Jarvis")
    Username = env_vars.get("Username", "User")
except Exception as e:
    print(f"Error loading .env file: {e}")
    Assistantname = "Jarvis"
    Username = "User"


current_dir = os.getcwd()
old_chat_message = ""
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"

# Ensure directories exist
os.makedirs(TempDirPath, exist_ok=True)
os.makedirs(GraphicsDirPath, exist_ok=True)

# Define color scheme
COLORS = {
    "background": "#121212",
    "primary": "#1E88E5",
    "secondary": "#0D47A1",
    "accent": "#64B5F6",
    "text_light": "#FFFFFF",
    "text_dark": "#121212",
    "success": "#4CAF50",
    "warning": "#FFC107",
    "error": "#F44336",
    "card_bg": "#1E1E1E",
    "border": "#333333",
    "user_message_bg": "#0D47A1",
    "assistant_message_bg": "#1E1E1E",
    "button_bg": "#2979FF",
    "button_hover": "#1565C0",
    "control_button": "#E0E0E0",
}

def AnswerModifier(Answer):
      lines = Answer.split('\n')
      non_empty_lines = [line for line in lines if line.strip()]
      modified_answer = '\n'.join(non_empty_lines)
      return modified_answer

def QueryModifier(Query):
      new_query = Query.lower().strip()
      query_words = new_query.split()
      question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

      if any(word + " " in new_query for word in question_words):
            if query_words[-1][-1] in ['.', '?', '!']:
                  new_query = new_query[:-1] + "?"
            else:
                  new_query += "?"
      else:
            if query_words[-1][-1] in ['.', '?', '!']:
                  new_query = new_query[:-1] + "."
            else:
                  new_query += "."
      return new_query.capitalize()

def SetMicrophoneStatus(Command):
      with open(rf"{TempDirPath}\Mic.data", "w", encoding="utf-8") as file:
            file.write(Command)

def GetMicrophoneStatus():
    try:
      with open(rf"{TempDirPath}\Mic.data", "r", encoding="utf-8") as file:
            Status = file.read()
      return Status
    except FileNotFoundError:
        with open(rf"{TempDirPath}\Mic.data", "w", encoding="utf-8") as file:
            file.write("True")
        return "True"

def SetAssistantStatus(Status):
      with open(rf"{TempDirPath}\Status.data", "w", encoding="utf-8") as file:
            file.write(Status)

def GetAssistantStatus():
    try:
      with open(rf"{TempDirPath}\Status.data", "r", encoding="utf-8") as file:
            Status = file.read()
      return Status
    except FileNotFoundError:
        with open(rf"{TempDirPath}\Status.data", "w", encoding="utf-8") as file:
            file.write("Available...")
        return "Available..."

def MicButtonInitiated():
      SetMicrophoneStatus("False")

def MicButtonClosed():
      SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
      Path = rf"{GraphicsDirPath}\{Filename}"
      return Path

def TempDirectoryPath(Filename):
      Path = rf"{TempDirPath}\{Filename}"
      return Path

def ShowTextToScreen(Text):
      with open(rf"{TempDirPath}\Responses.data", "w", encoding="utf-8") as file:
            file.write(Text)

def SaveTextInput(text):
    """Save text input to be processed by the main application"""
    with open(rf"{TempDirPath}\TextInput.data", "w", encoding="utf-8") as file:
        file.write(text)

class MessageBubble(QFrame):
    def __init__(self, message, is_user=False):
        super().__init__()
        self.is_user = is_user
        self.message = message
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        
        # Create message text
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        # Set font
        font = QFont()
        font.setPointSize(11)
        message_label.setFont(font)
        
        # Set style based on sender
        if self.is_user:
            self.setStyleSheet(f"""
                background-color: {COLORS['user_message_bg']};
                border-radius: 15px;
                color: {COLORS['text_light']};
                margin-left: 50px;
            """)
        else:
            self.setStyleSheet(f"""
                background-color: {COLORS['assistant_message_bg']};
                border-radius: 15px;
                color: {COLORS['text_light']};
                margin-right: 50px;
                border: 1px solid {COLORS['border']};
            """)
        
        layout.addWidget(message_label)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        self.initUI()
        
    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create scroll area for messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Create container for messages
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setAlignment(Qt.AlignTop)
        self.messages_layout.setSpacing(15)
        self.messages_layout.setContentsMargins(10, 10, 10, 10)
        
        # Set the container as the scroll area widget
        self.scroll_area.setWidget(self.messages_container)
        
        # Create text input area
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(5, 5, 5, 5)
        input_layout.setSpacing(10)
        
        # Create text input field
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type your message here...")
        self.text_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['card_bg']};
                color: {COLORS['text_light']};
                border: 1px solid {COLORS['border']};
                border-radius: 20px;
                padding: 10px 15px;
                font-size: 14px;
                min-height: 24px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['accent']};
            }}
        """)
        self.text_input.returnPressed.connect(self.send_message)
        
        # Create send button
        send_button = QPushButton()
        send_button.setIcon(QIcon(GraphicsDirectoryPath("Chats.png")))  # Use an existing icon or create a send icon
        send_button.setIconSize(QSize(24, 24))
        send_button.setFixedSize(40, 40)
        send_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['button_bg']};
                border-radius: 20px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['button_hover']};
            }}
        """)
        send_button.clicked.connect(self.send_message)
        
        # Add widgets to input layout
        input_layout.addWidget(self.text_input, 1)
        input_layout.addWidget(send_button, 0)
        
        # Create bottom bar with status and controls
        bottom_bar = QWidget()
        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(10, 5, 10, 5)
        
        # Create status label
        self.status_label = QLabel("Available...")
        self.status_label.setStyleSheet(f"color: {COLORS['accent']}; font-size: 14px;")
        
        # Create animated gif
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet('border: none;')
        movie = QMovie(GraphicsDirectoryPath("Jarvis.gif"))
        max_gif_size = 60
        movie.setScaledSize(QSize(max_gif_size, max_gif_size))
        self.gif_label.setMovie(movie)
        movie.start()
        
        # Create microphone button
        mic_button = QPushButton()
        mic_icon = QIcon(GraphicsDirectoryPath("Mic_on.png"))
        mic_button.setIcon(mic_icon)
        mic_button.setIconSize(QSize(30, 30))
        mic_button.setFixedSize(50, 50)
        mic_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['button_bg']};
                border-radius: 25px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['button_hover']};
            }}
        """)
        
        # Toggle mic on click
        self.mic_toggled = False
        mic_button.clicked.connect(self.toggle_mic)
        
        # Add widgets to bottom layout
        bottom_layout.addWidget(self.status_label, 0)
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(self.gif_label, 0)
        bottom_layout.addWidget(mic_button, 0)
        
        # Add widgets to main layout
        main_layout.addWidget(self.scroll_area, 1)
        main_layout.addWidget(input_container, 0)
        main_layout.addWidget(bottom_bar, 0)
        
        # Set background color
        self.setStyleSheet(f"background-color: {COLORS['background']};")
        
        # Set up timer to check for new messages
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.updateStatus)
        self.timer.start(100)
        
        # Apply scrollbar styling
        self.scroll_area.setStyleSheet(f"""
            QScrollBar:vertical {{
                  border: none;
                background: {COLORS['background']};
                width: 8px;
                  margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['accent']};
                  min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                  border: none;
                  background: none;
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                  background: none;
            }}
        """)
    
    def send_message(self):
        """Send the message from the text input field"""
        text = self.text_input.text().strip()
        if text:
            # Save the text input to be processed by the main application
            SaveTextInput(text)
            
            # Clear the input field
            self.text_input.clear()
            
            # Set status to indicate processing
            SetAssistantStatus("Processing your message...")
    
    def toggle_mic(self):
        if self.mic_toggled:
            MicButtonClosed()
            self.status_label.setText("Listening...")
        else:
            MicButtonInitiated()
            self.status_label.setText("Microphone off")
        
        self.mic_toggled = not self.mic_toggled
    
    def updateStatus(self):
        status = GetAssistantStatus()
        self.status_label.setText(status)
    
    def loadMessages(self):
        global old_chat_message
        try:
            with open(TempDirectoryPath('Responses.data'), "r", encoding="utf-8") as file:
                messages = file.read()
            
            if messages and messages != old_chat_message:
                # Clear existing messages
                self.clearMessages()
                
                # Parse and add messages
                message_pairs = []
                lines = messages.split('\n')
                current_speaker = None
                current_message = []
                
                for line in lines:
                    if line.strip():
                        if f"{Username} :" in line:
                            if current_speaker and current_message:
                                message_pairs.append((current_speaker, ' '.join(current_message)))
                            current_speaker = "user"
                            current_message = [line.split(f"{Username} : ", 1)[1]]
                        elif f"{Assistantname} :" in line:
                            if current_speaker and current_message:
                                message_pairs.append((current_speaker, ' '.join(current_message)))
                            current_speaker = "assistant"
                            current_message = [line.split(f"{Assistantname} : ", 1)[1]]
                        else:
                            current_message.append(line)
                
                if current_speaker and current_message:
                    message_pairs.append((current_speaker, ' '.join(current_message)))
                
                # Add message bubbles
                for speaker, message in message_pairs:
                    self.addMessage(message, speaker == "user")
                
                # Scroll to bottom
                self.scroll_area.verticalScrollBar().setValue(
                    self.scroll_area.verticalScrollBar().maximum()
                )
                
                old_chat_message = messages
        except Exception as e:
            print(f"Error loading messages: {e}")
    
    def clearMessages(self):
        # Clear all message bubbles
        while self.messages_layout.count():
            item = self.messages_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    def addMessage(self, message, is_user=False):
        bubble = MessageBubble(message, is_user)
        self.messages_layout.addWidget(bubble)

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Create welcome text
        welcome_label = QLabel(f"Welcome to {Assistantname}")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet(f"""
            color: {COLORS['text_light']};
            font-size: 36px;
            font-weight: bold;
            margin-top: 50px;
        """)
        
        # Create subtitle
        subtitle_label = QLabel("Your AI Assistant")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet(f"""
            color: {COLORS['accent']};
            font-size: 24px;
            margin-bottom: 30px;
        """)
        
        # Create GIF container
        gif_container = QWidget()
        gif_layout = QVBoxLayout(gif_container)
        gif_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add GIF
        gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath("Jarvis.gif"))
        max_gif_size = int(min(screen_width, screen_height) * 0.3)  # Reduced from 0.4
        movie.setScaledSize(QSize(max_gif_size, max_gif_size))
        gif_label.setMovie(movie)
        movie.start()
        gif_label.setAlignment(Qt.AlignCenter)
        
        # Add status label
        self.status_label = QLabel("Available...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(f"""
            color: {COLORS['accent']};
            font-size: 18px;
            margin-top: 20px;
        """)
        
        # Add mic button
        self.icon_label = QPushButton()
        self.icon_label.setIcon(QIcon(GraphicsDirectoryPath("Mic_on.png")))
        self.icon_label.setIconSize(QSize(50, 50))
        self.icon_label.setFixedSize(80, 80)
        self.icon_label.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['button_bg']};
                border-radius: 40px;
                padding: 15px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['button_hover']};
            }}
        """)
        self.toggled = True
        self.icon_label.clicked.connect(self.toggle_icon)
        
        # Add widgets to gif container
        gif_layout.addWidget(gif_label, 0, Qt.AlignCenter)
        gif_layout.addWidget(self.status_label, 0, Qt.AlignCenter)
        gif_layout.addWidget(self.icon_label, 0, Qt.AlignCenter)
        
        # Add all elements to main layout
        main_layout.addWidget(welcome_label)
        main_layout.addWidget(subtitle_label)
        main_layout.addWidget(gif_container, 1)
        
        # Set up the widget
        self.setStyleSheet(f"background-color: {COLORS['background']};")
        
        # Set up timer to update status
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateStatus)
        self.timer.start(100)
    
    def updateStatus(self):
        status = GetAssistantStatus()
        self.status_label.setText(status)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.icon_label.setIcon(QIcon(GraphicsDirectoryPath("Mic_off.png")))
            MicButtonInitiated()
        else:
            self.icon_label.setIcon(QIcon(GraphicsDirectoryPath("Mic_on.png")))
            MicButtonClosed()
        
        self.toggled = not self.toggled

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        
        self.setStyleSheet(f"background-color: {COLORS['background']};")

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.initUI()
        self.current_screen = None
        self.stacked_widget = stacked_widget
        
    def initUI(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Create title with logo
        title_layout = QHBoxLayout()
        logo_label = QLabel()
        logo_pixmap = QPixmap(GraphicsDirectoryPath("Jarvis.gif")).scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        
        title_label = QLabel(f" {Assistantname} AI")
        title_label.setStyleSheet(f"color: {COLORS['text_light']}; font-size: 16px; font-weight: bold;")
        
        title_layout.addWidget(logo_label)
        title_layout.addWidget(title_label)
        title_layout.addStretch(1)
        
        # Create navigation buttons
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(15)
        
        home_button = QPushButton("Home")
        home_button.setIcon(QIcon(GraphicsDirectoryPath("Home.png")))
        home_button.setCursor(Qt.PointingHandCursor)
        
        chat_button = QPushButton("Chat")
        chat_button.setIcon(QIcon(GraphicsDirectoryPath("Chats.png")))
        chat_button.setCursor(Qt.PointingHandCursor)
        
        # Style buttons
        button_style = f"""
            QPushButton {{
                background-color: {COLORS['button_bg']};
                color: {COLORS['text_light']};
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {COLORS['button_hover']};
            }}
        """
        home_button.setStyleSheet(button_style)
        chat_button.setStyleSheet(button_style)
        
        # Connect buttons
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        chat_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        
        nav_layout.addWidget(home_button)
        nav_layout.addWidget(chat_button)
        
        # Create window control buttons
        control_layout = QHBoxLayout()
        control_layout.setSpacing(15)

        minimize_button = QPushButton()
        minimize_button.setIcon(QIcon(GraphicsDirectoryPath("Minimize2.png")))
        minimize_button.setFixedSize(30, 30)
        minimize_button.setCursor(Qt.PointingHandCursor)
        
        self.maximize_button = QPushButton()
        self.maximize_button.setIcon(QIcon(GraphicsDirectoryPath("Maximize.png")))
        self.maximize_button.setFixedSize(30, 30)
        self.maximize_button.setCursor(Qt.PointingHandCursor)

        close_button = QPushButton()
        close_button.setIcon(QIcon(GraphicsDirectoryPath("Close.png")))
        close_button.setFixedSize(30, 30)
        close_button.setCursor(Qt.PointingHandCursor)
        
        # Style control buttons - improved visibility
        control_button_style = f"""
            QPushButton {{
                background-color: {COLORS['control_button']};
                border-radius: 15px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['border']};
            }}
        """
        minimize_button.setStyleSheet(control_button_style)
        self.maximize_button.setStyleSheet(control_button_style)
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['control_button']};
                border-radius: 15px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['error']};
            }}
        """)
        
        # Connect control buttons
        minimize_button.clicked.connect(self.minimizeWindow)
        self.maximize_button.clicked.connect(self.maximizeWindow)
        close_button.clicked.connect(self.closeWindow)

        control_layout.addWidget(minimize_button)
        control_layout.addWidget(self.maximize_button)
        control_layout.addWidget(close_button)
        
        # Add all layouts to main layout
        layout.addLayout(title_layout)
        layout.addStretch(1)
        layout.addLayout(nav_layout)
        layout.addStretch(1)
        layout.addLayout(control_layout)
        
        # Set up dragging
        self.draggable = True
        self.offset = None
        
        # Style the top bar
        self.setStyleSheet(f"""
            background-color: {COLORS['card_bg']};
            border-bottom: 1px solid {COLORS['border']};
        """)
        self.setFixedHeight(60)  # Increased from 50
      
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(COLORS['card_bg']))
        super().paintEvent(event)

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(QIcon(GraphicsDirectoryPath("Maximize.png")))
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(QIcon(GraphicsDirectoryPath("Minimize.png")))

    def closeWindow(self):
        self.parent().close()

    def mousePressEvent(self, event):
        if self.draggable:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        # Create stacked widget for screens
        self.stacked_widget = QStackedWidget(self)
        
        # Create screens
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        
        # Add screens to stacked widget
        self.stacked_widget.addWidget(initial_screen)
        self.stacked_widget.addWidget(message_screen)
        
        # Set window properties - adjusted size ratio
        window_width = int(screen_width * 0.7)  # Changed from 0.8
        window_height = int(screen_height * 0.8)
        self.setGeometry((screen_width - window_width) // 2, (screen_height - window_height) // 2, 
                         window_width, window_height)
        self.setStyleSheet(f"background-color: {COLORS['background']};")
        
        # Create and set top bar
        top_bar = CustomTopBar(self, self.stacked_widget)
        self.setMenuWidget(top_bar)
        
        # Set central widget
        self.setCentralWidget(self.stacked_widget)

def GraphicalUserInterface():
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Try to load fonts, but use system fonts if they're not available
    try:
        font_dir = os.path.join(current_dir, "Frontend", "Fonts")
        os.makedirs(font_dir, exist_ok=True)
        
        # Check if fonts exist, otherwise use system fonts
        roboto_regular = os.path.join(font_dir, "Roboto-Regular.ttf")
        roboto_bold = os.path.join(font_dir, "Roboto-Bold.ttf")
        
        if os.path.exists(roboto_regular):
            QFontDatabase.addApplicationFont(roboto_regular)
        if os.path.exists(roboto_bold):
            QFontDatabase.addApplicationFont(roboto_bold)
    except Exception as e:
        print(f"Error loading fonts: {e}")
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()










