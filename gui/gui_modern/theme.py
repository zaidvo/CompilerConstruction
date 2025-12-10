"""
Theme Configuration for Modern GUI
Deep purple, gold, and teal color scheme
"""

class ModernTheme:
    """Color scheme and styling constants"""
    
    # Primary Colors
    DEEP_PURPLE = '#6200EA'
    LIGHT_PURPLE = '#7C4DFF'
    GOLD = '#FFD700'
    TEAL = '#00D4AA'
    HOT_PINK = '#FF1493'
    
    # Background Colors
    DARK_NAVY = '#1e1e2e'
    DARKER_NAVY = '#181825'
    PANEL_BG = '#2d2d44'
    SECTION_HEADER = '#3a3a5a'
    
    # Syntax Highlighting Colors
    SYNTAX_KEYWORD = '#FF1493'    # Hot pink
    SYNTAX_NUMBER = '#FFD700'     # Golden yellow
    SYNTAX_STRING = '#00FF7F'     # Bright green
    SYNTAX_COMMENT = '#00FFFF'    # Cyan
    SYNTAX_IDENTIFIER = '#E0E0E0' # Light gray
    SYNTAX_OPERATOR = '#FF6B6B'   # Coral
    
    # Phase Button Colors
    PHASE_LEX = '#00D4AA'        # Cyan/Teal
    PHASE_PARSE = '#9B59B6'      # Purple
    PHASE_CHECK = '#FF8C00'      # Orange
    PHASE_IR = '#FF6B6B'         # Coral
    PHASE_OPT = '#00FF7F'        # Green
    PHASE_RUN = '#FF1493'        # Pink
    
    # UI Element Colors
    BUTTON_HOVER = '#5A5A7A'
    SCROLLBAR_BG = '#2d2d44'
    SCROLLBAR_FG = '#6200EA'
    TEXT_FG = '#E0E0E0'
    TEXT_DISABLED = '#808080'
    
    # Status Colors
    SUCCESS = '#00FF7F'
    ERROR = '#FF4444'
    WARNING = '#FFD700'
    INFO = '#00D4AA'
    
    # Fonts
    FONT_FAMILY = 'Consolas'
    FONT_SIZE = 11
    FONT_SIZE_LARGE = 13
    FONT_SIZE_SMALL = 9
    
    @staticmethod
    def get_phase_color(phase_num):
        """Get color for phase button by number"""
        colors = [
            ModernTheme.PHASE_LEX,
            ModernTheme.PHASE_PARSE,
            ModernTheme.PHASE_CHECK,
            ModernTheme.PHASE_IR,
            ModernTheme.PHASE_OPT,
            ModernTheme.PHASE_RUN
        ]
        if 0 <= phase_num < len(colors):
            return colors[phase_num]
        return ModernTheme.DEEP_PURPLE
