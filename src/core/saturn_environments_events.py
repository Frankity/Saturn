from src.utils.database import EnvironmentVars


class SaturnEvents:
    def __init__(self):
        self.env_vars = {}

    def set_env_var(self, name, value):
        result = (EnvironmentVars
                  .insert(key=name, initial_value=value, final_value=value, enabled=True, environment=1)
                  .execute())
        self.env_vars[name] = value

    def get_env_var(self, name, default=None):
        return self.env_vars.get(name, default)

    def get_all_vars(self):
        return self.env_vars
