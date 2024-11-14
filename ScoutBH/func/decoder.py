from func.res import attr_factors
from func.res import attr_names
from func.res import attr_upgrade_gains
from func.res import attr_random_stats
from func.res import item_info
import math



class APIDecoder:
    def __init__(self):
        self.attr_factors = attr_factors.attr_factors
        self.upgrade_gains = attr_upgrade_gains.upgrade_gains
        self.random_stats = attr_random_stats.random_stats 
        self.random_stats_keys = sorted(list(self.random_stats.keys()))
        self.attr_info = attr_names.attr_info
        self.item_info = item_info.item_info
        

    def get_attr_ID(self, value):
        return self.random_stats_keys[int((value / 101) * len(self.random_stats))]

    def decode(self, data, maxtier=False):
        if data["type"] not in self.attr_factors.keys():
            return {
                'bonus_attr_keys' : [],
                "type" : None   
            }

        item_data = {
            'ID' : data['id'],
            'deleted' : 0,
            'forsale' : 0,
            'type' : data['type'],
            'tier' : data['tier'],
            'upgrade' : data['upgrade'],
            'quality' : 0,
            'level' : 0,
            'bonus_attr_keys' : [],
            'attr' : {},
            'name' : self.item_info[data['type']][data['tier']],
            'attr_IDs' : [],
            'owner' : 0,
            'rolls' : data['rolls'],
            'slot' : data['slot'],
            'bound' : data['bound'],
            'stacks' : data['stacks'],
            "gearscore" : 0
        }

        if maxtier:
            data["tier"] = list(self.item_info[data['type']].keys())[-1]

        attr_data = self.attr_factors[data['type']]

        item_data['level'] = attr_data['baselvl'] + int(data['tier'] / attr_data['tiers'] * 100)
        roll_idx = 0
        item_data['quality'] = data['rolls'][roll_idx]
        roll_idx += 1
        for stat_key, stat in attr_data['stats'].items():
            stat_min = stat['base'] + item_data['level'] * stat['min']
            stat_max = stat['base'] + (item_data['level'] + 10) * stat['max']
            stat_val = stat_min
            stat_val += (stat_max - stat_min) * math.pow(item_data['quality'] / 100, 2)
            stat_val += self.upgrade_gains[stat['id']] * item_data['upgrade']
            stat_val = int(stat_val)
            if stat_key != "att":
                if item_data["type"] == "shield":
                    m = 0.5
                elif item_data["type"] == "orb":
                    m = 0.7
                else:
                    m = 1
                item_data["gearscore"] += m * (stat_val / self.upgrade_gains[stat["id"]])

            item_data['attr'][stat_key] = {
                'value' : stat_val * self.attr_info[stat['id']]['*'],
                'quality' : item_data['quality'],
                'bonus' : False,
                'attr_info' : self.attr_info[stat['id']]
            }
            item_data['attr_IDs'].append(stat['id'])

        n_attr_bonus = round((item_data['quality'] / 100) ** 1.5 * 3.6)
        # TODO
        if item_data['quality'] < 50:
            item_data['tier_quality'] = 0
        elif item_data['quality'] < 70:
            item_data['tier_quality'] = 1
        elif item_data['quality'] < 90:
            item_data['tier_quality'] = 2
        else:
            item_data['tier_quality'] = 3
        for roll_ID in range(n_attr_bonus):
            value = data['rolls'][roll_idx] # i
            roll_idx += 1
            attr_ID = self.get_attr_ID(value)
            while attr_ID in item_data['attr_IDs']:
                attr_ID = self.get_attr_ID(value)
                value = (value + 5) % 100

            attr_quality = (data['rolls'][roll_idx] + item_data['quality']) / 2
            roll_idx += 1
            attr_stat = self.random_stats[attr_ID]
            attr_upgrade_gains = self.upgrade_gains[attr_ID]
            attr_bonus = attr_stat['min'] + (attr_stat['max'] - attr_stat['min']) * math.pow(attr_quality / 100, 2)
            attr_bonus *= item_data['level'] * attr_data['weight']
            attr_value = math.ceil(max(attr_bonus, attr_upgrade_gains) + attr_upgrade_gains * item_data['upgrade'])
            item_data["gearscore"] += attr_value / self.upgrade_gains[attr_ID]
            attr_name = self.attr_info[attr_ID]['short']
            item_data['bonus_attr_keys'].append(attr_name)
            item_data['attr'][attr_name] = {
                'value' : attr_value * self.attr_info[attr_ID]['*'],
                'quality' : attr_quality,
                'bonus' : True,
                'attr_info' : self.attr_info[attr_ID]
            }
            item_data['attr_IDs'].append(attr_ID)
            
        item_data["gearscore"] = int(round(item_data["gearscore"]))

        return item_data

    def get_default_deleted(self, item_ID):
        return {
            'ID' : item_ID,
            'deleted' : 1,
            'forsale' : 0,
            'type' : 'unknown',
            'tier' : 0,
            'upgrade' : 0,
            'quality' : 0,
            'level' : 0,
            'bonus_attr_keys' : [],
            'attr' : {},
            'name' : 'unknown',
            'attr_IDs' : [],
            'owner' : 0,
            'rolls' : [],
            'slot' : 0,
            'bound' : 0,
            'stacks' : None,
            'tier_quality' : 0
        }

    def print(self, item_data):
        msg = ''
        msg += f'{item_data["name"]} +{item_data["upgrade"]}'
        msg += f' {item_data["quality"]}%\n'
        for attr_type, attr_info in item_data['attr'].items():
            msg += f'\t{attr_info["value"]} {attr_type}'
            msg += f' ({attr_info["quality"]}%)\n' if attr_info['bonus'] else '\n'
        msg += f'iID: {item_data["ID"]}\n'
        print(msg)
