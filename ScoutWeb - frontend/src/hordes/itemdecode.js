import attr_factors from "./res/attr_factors.js"
import upgrade_gains from "./res/attr_upgrade_gains.js"
import random_stats from "./res/attr_random_stats.js"
import attr_info from "./res/attr_names.js"
import item_info from "./res/item_info.js"


export default function decode(data, params) {
    if (!Object.keys(attr_factors).includes(data["type"])) {
        return null
    }

    var item_data = {
        'ID' : data['id'],
        'deleted' : 0,
        'forsale' : 0,
        'type' : data['type'],
        'tier' : data['tier'],
        'upgrade' : params.maxupgrade ? 7 : data['upgrade'],
        'quality' : 0,
        'level' : 0,
        'bonus_attr_keys' : [],
        'attr' : {},
        'name' : item_info[data['type']][data['tier']],
        'attr_IDs' : [],
        'owner' : 0,
        'rolls' : data['rolls'],
        'slot' : data['slot'],
        'bound' : data['bound'],
        'stacks' : data['stacks'],
        "gearscore" : 0
    }

    var attr_data = attr_factors[data['type']]

    item_data['level'] = attr_data['baselvl'] + Math.floor(data['tier'] / attr_data['tiers'] * 100)
    var roll_idx = 0
    item_data['quality'] = data['rolls'][roll_idx]
    roll_idx += 1
    for (const [stat_key, stat] of Object.entries(attr_data['stats'])) {
        var stat_min = stat['base'] + item_data['level'] * stat['min']
        var stat_max = stat['base'] + (item_data['level'] + 10) * stat['max']
        var stat_val = stat_min
        stat_val += (stat_max - stat_min) * Math.pow(item_data['quality'] / 100, 2)
        stat_val += upgrade_gains[stat['id']] * item_data['upgrade']
        stat_val = Math.floor(stat_val)

        if (stat_key != "att") {
            var m
            if (item_data["type"] == "shield") {
                m = 0.5
            } else if (item_data["type"] == "orb") {
                m = 0.7
            } else {
                m = 1
            }
            item_data["gearscore"] += m * (stat_val / upgrade_gains[stat["id"]])
        }

        item_data['attr'][stat_key] = {
            'value' : stat_val * attr_info[stat['id']]['*'],
            'quality' : item_data['quality'],
            'bonus' : false,
            'attr_info' : attr_info[stat['id']]
        }
        item_data['attr_IDs'].push(stat['id'])
    }

    var n_attr_bonus = Math.round((item_data['quality'] / 100) ** 1.5 * 3.6)

    if (item_data['quality'] < 50) {
        item_data['tier_quality'] = 0   
    } else if (item_data['quality'] < 70) {
        item_data['tier_quality'] = 1
    } else if (item_data['quality'] < 90) {
        item_data['tier_quality'] = 2
    } else {
        item_data['tier_quality'] = 3
    }

    for (let roll_ID = 0; roll_ID < n_attr_bonus; roll_ID++) {
        var value = data['rolls'][roll_idx]
        roll_idx += 1
        var attr_ID = Object.keys(random_stats)[Math.floor((value / 101) * Object.keys(random_stats).length)]
        while (item_data['attr_IDs'].includes(attr_ID)) {
            attr_ID = Object.keys(random_stats)[Math.floor((value / 101) * Object.keys(random_stats).length)]
            value = (value + 5) % 100
        }

        var attr_quality = (data['rolls'][roll_idx] + item_data['quality']) / 2
        roll_idx += 1
        var attr_stat = random_stats[attr_ID]
        var attr_upgrade_gains = upgrade_gains[attr_ID]
        var attr_bonus = attr_stat['min'] + (attr_stat['max'] - attr_stat['min']) * Math.pow(attr_quality / 100, 2)
        attr_bonus *= item_data['level'] * attr_data['weight']
        var attr_value = Math.ceil(Math.max(attr_bonus, attr_upgrade_gains) + attr_upgrade_gains * item_data['upgrade'])
        item_data["gearscore"] += attr_value / upgrade_gains[attr_ID]
        var attr_name = attr_info[attr_ID]['short']
        item_data['bonus_attr_keys'].push(attr_name)
        item_data['attr'][attr_name] = {
            'value' : attr_value * attr_info[attr_ID]['*'],
            'quality' : attr_quality,
            'bonus' : true,
            'attr_info' : attr_info[attr_ID]
        }
        item_data['attr_IDs'].push(attr_ID) 
    }

    item_data["gearscore"] = Math.round(item_data["gearscore"])

    return item_data

}
