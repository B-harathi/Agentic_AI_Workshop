class StateFlow:
    def __init__(self):
        self.current_state = "INIT"
        self.user_data = {}
        self.analysis_result = None
        self.strategy = None
        self.recommendations = None
    def set_user_data(self, data):
        self.user_data = data
        self.current_state = "USER_DATA_LOADED"
    def set_analysis_result(self, result):
        self.analysis_result = result
        self.current_state = "ANALYSIS_COMPLETE"
    def set_strategy(self, strategy):
        self.strategy = strategy
        self.current_state = "STRATEGY_DETERMINED"
    def set_recommendations(self, recommendations):
        self.recommendations = recommendations
        self.current_state = "RECOMMENDATIONS_READY"
    def get_next_agent(self):
        if self.current_state == "INIT":
            return "PortfolioAnalyst"
        elif self.current_state == "ANALYSIS_COMPLETE":
            return "GrowthStrategist" if self.strategy == "Growth" else "ValueStrategist"
        elif self.current_state == "RECOMMENDATIONS_READY":
            return "FinancialAdvisor"
        else:
            return None

state_flow = StateFlow() 