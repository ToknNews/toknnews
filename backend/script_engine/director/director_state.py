from datetime import datetime, timedelta


class DirectorState:
    """
    Tracks everything the Programming Director needs to know between decisions.
    """

    def __init__(self) -> None:
        # Last segment type (news, banter, panel, ad_break, etc.)
        self.last_segment: str | None = None

        # Timing for promos / ads / banter / resets
        now = datetime.utcnow()
        self.last_ad_time: datetime = now - timedelta(minutes=10)
        self.last_promo_time: datetime = now - timedelta(minutes=10)
        self.last_banter_time: datetime = now - timedelta(minutes=5)
        self.last_reset_time: datetime = now
        self.reset_cooldown_seconds: int = 300  # 5-minute minimum between resets
        self.last_intro_time: datetime = now
        self.intro_interval_minutes: int = 10     # how often to restart show
        self.reset_interval_minutes: int = 5     # how often to soft-reset
        self.escalation_level: int = 0
        self.reset_suppression_cycles = 0   # Number of cycles after reset where escalation is ignored
        self.ad_suppression_cycles = 0   # number of cycles during which ads are disabled


        # Cast usage/fatigue tracking
        # e.g. {"Chip Blue": 5, "Neura Grey": 3}
        self.cast_usage: dict[str, int] = {}
        self.cast_cooldowns: dict[str, datetime] = {}

        # Sentiment + segment history
        # e.g. ["positive", "negative", ...]
        self.sentiment_window: list[str] = []
        # e.g. ["news", "panel", "banter", ...]
        self.segment_history: list[str] = []

        # Mode: "shortform", "longform", "continuous"
        self.show_mode: str = "longform"

        # Memory hooks (wired up later)
        self.daily_memory: dict = {}
        self.weekly_memory: dict = {}
        self.lore_memory: dict = {}

        # Breaking news queue (list of story dicts)
        self.breaking_queue: list[dict] = []
