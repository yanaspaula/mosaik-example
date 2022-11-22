# controller.py
"""
Um modelo de controle simples.

Verifica se o valor *val_in* recebido de uma instância de modelo está entre [-3, 3].
"""
import mosaik_api

META = {
    'type': 'event-based',      # Necessário para same-time loop
    'models': {
        'Agent': {
            'public': True,
            'params': [],
            'attrs': ['val_in', 'delta'],
        },
    },
}

class Controller(mosaik_api.Simulator):
    def __init__(self):
        super().__init__(META)
        self.agents = []
        self.data = {}
        self.time = 0

    def create(self, num, model):
        n_agents = len(self.agents)
        entities = []
        for i in range(n_agents, n_agents + num):
            eid = 'Agent_%d' % i
            self.agents.append(eid)
            entities.append({'eid': eid, 'type': model})

        return entities

    def step(self, time, inputs, max_advance):
        print('[controller_demo_3] max_advance: {}'.format(max_advance))
        self.time = time
        data = {}
        for agent_eid, attrs in inputs.items():
            '''
                Verifica se há valores disponíveis de *delta* por evento.
                Caso haja dados disponíveis pelo controlador-mestre, 
                o controlador não calcula o *delta* e apenas recebe 
                o valor disponível do mestre
            '''
            delta_dict = attrs.get('delta', {})
            if len(delta_dict) > 0:     
                data[agent_eid] = {'delta': list(delta_dict.values())[0]}   # Esvazia dicionário data para same-time loop
                continue

            values_dict = attrs.get('val_in', {})
            if len(values_dict) != 1:
                raise RuntimeError('Only one ingoing connection allowed per '
                                   'agent, but "%s" has %i.'
                                   % (agent_eid, len(values_dict)))
            value = list(values_dict.values())[0]

            # Limita os valores de *val* dentro do intervalo [-3, 3]
            if value >= 3:
                delta = -1
            elif value <= -3:
                delta = 1
            else:
                continue

            data[agent_eid] = {'delta': delta}

        self.data = data

        return None

    def get_data(self, outputs):
        data = {}
        for agent_eid, attrs in outputs.items():
            for attr in attrs:
                if attr != 'delta':
                    raise ValueError('Unknown output attribute "%s"' % attr)
                if agent_eid in self.data:
                    data['time'] = self.time        # Necessário para same-time loop
                    data.setdefault(agent_eid, {})[attr] = self.data[agent_eid][attr]

        return data


def main():
    return mosaik_api.start_simulation(Controller())


if __name__ == '__main__':
    main()