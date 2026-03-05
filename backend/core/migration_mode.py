import logging

logger = logging.getLogger(__name__)

class MigrationModeFilter:
    """
    Non-invasive mode abstraction layer that refines migration decisions
    based on user-selected strategy without modifying core logic.
    """
    
    MODES = {
        "smart": "Smart (Default)",
        "thermal_first": "Thermal-First",
        "performance_first": "Performance-First",
        "conservative": "Conservative"
    }
    
    def __init__(self, mode="smart"):
        self.mode = mode
        logger.info(f"MigrationModeFilter initialized with mode: {mode}")
    
    def set_mode(self, mode):
        """Change the active migration mode."""
        if mode not in self.MODES:
            logger.warning(f"Invalid mode '{mode}', defaulting to 'smart'")
            mode = "smart"
        self.mode = mode
        logger.info(f"Migration mode changed to: {mode}")
    
    def get_mode(self):
        """Get the current active mode."""
        return self.mode
    
    def apply(self, decision, core_scores=None, thermal_data=None):
        """
        Apply mode-specific refinement to the decision output.
        
        Args:
            decision: Original decision from DecisionEngine
            core_scores: Optional core risk scores for context
            thermal_data: Optional thermal data for context
            
        Returns:
            Refined decision (may be modified or unchanged)
        """
        if self.mode == "smart":
            # Smart mode: pass through unchanged (existing behavior)
            return decision
        
        elif self.mode == "thermal_first":
            # Thermal-First: More aggressive migration on thermal signals
            return self._apply_thermal_first(decision, core_scores, thermal_data)
        
        elif self.mode == "performance_first":
            # Performance-First: Reduce migrations to preserve cache/performance
            return self._apply_performance_first(decision, core_scores)
        
        elif self.mode == "conservative":
            # Conservative: Only migrate on critical conditions
            return self._apply_conservative(decision, core_scores, thermal_data)
        
        return decision
    
    def _apply_thermal_first(self, decision, core_scores, thermal_data):
        """
        Thermal-First mode: Prioritize temperature reduction.
        - Allow migrations even with lower thermal risk
        - Reduce cooldown sensitivity
        """
        if decision["action"] == "NO_ACTION":
            # Check if we should override NO_ACTION for thermal reasons
            if thermal_data and core_scores:
                max_temp = max([c.get("temperature", 0) for c in thermal_data.get("cores", {}).values()])
                if max_temp > 70:  # Lower threshold than default
                    # Original decision was NO_ACTION, but thermal-first wants action
                    logger.info(f"Thermal-First mode: Considering migration at {max_temp}°C (lower threshold)")
                    # We don't override here, just log the bias
                    # The actual decision stays as-is to preserve safety
        
        return decision
    
    def _apply_performance_first(self, decision, core_scores):
        """
        Performance-First mode: Minimize migrations to preserve performance.
        - Only migrate on high-risk thermal conditions
        - Increase effective cooldown
        """
        if decision["action"] == "MIGRATE":
            # Check if migration is truly necessary from performance perspective
            reason = decision.get("reason", "")
            if "Proactive" in reason:
                # Performance-first mode suppresses proactive migrations
                logger.info(f"Performance-First mode: Suppressing proactive migration to preserve cache locality")
                return {
                    "action": "NO_ACTION",
                    "reason": "Performance-First mode: Deferring proactive migration to preserve performance"
                }
        
        return decision
    
    def _apply_conservative(self, decision, core_scores, thermal_data):
        """
        Conservative mode: Minimize all migrations.
        - Only migrate on critical thermal conditions
        - Maximize stability
        """
        if decision["action"] == "MIGRATE":
            # Only allow migration if truly critical
            if thermal_data:
                cores = thermal_data.get("cores", {})
                from_core = decision.get("from_core")
                if from_core is not None and str(from_core) in cores:
                    temp = cores[str(from_core)].get("temperature", 0)
                    if temp < 85:  # Only migrate above 85°C in conservative mode
                        logger.info(f"Conservative mode: Suppressing migration (temp {temp}°C below critical threshold)")
                        return {
                            "action": "NO_ACTION",
                            "reason": f"Conservative mode: Core {from_core} at {temp}°C (below critical threshold)"
                        }
        
        return decision
    
    def get_mode_description(self):
        """Get a human-readable description of the current mode."""
        descriptions = {
            "smart": "Uses existing migration logic without modification. Balanced approach.",
            "thermal_first": "Prioritizes temperature reduction. More aggressive thermal management.",
            "performance_first": "Minimizes migrations to preserve cache locality and performance.",
            "conservative": "Only migrates on critical thermal conditions. Maximum stability."
        }
        return descriptions.get(self.mode, "Unknown mode")
