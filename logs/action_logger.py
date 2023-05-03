from matrx.logger.logger import GridWorldLogger


class ActionLogger(GridWorldLogger):
    # def __init__(self, save_path="", file_name_prefix="", file_extension=".csv", delimiter=";"):
    #     super.__init__(save_path=save_path, file_name_prefix=file_name_prefix,
    #                    file_extension=file_extension, delimiter=delimiter, log_strategy=1)

    def log(self, grid_world, agent_data):
        log_data = {}

        for agent_id, agent_body in grid_world.registered_agents.items():
            if 'human' or 'agent' in agent_id:
                log_data[agent_id + '_action'] = agent_body.current_action
                # log_data[agent_id + '_action_result'] = None
                # if agent_body.action_result is not None:
                #     log_data[agent_id + '_action_result'] = agent_body.action_result.succeeded
                log_data[agent_id + '_location'] = agent_body.location
                log_data[agent_id + 'nr_victims'] = agent_body.custom_properties['nr_victims']
                log_data[agent_id + 'score'] = agent_body.custom_properties['score']


        return log_data
