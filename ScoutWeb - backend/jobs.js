const cron = require("node-cron")
var axios = require('axios')
var { MongoClient } = require("mongodb");
var fs = require('fs');


const mongo = {
    client : new MongoClient("")
}


exports.initScheduledJobs = () => {
    const gloom = cron.schedule("0 */3 * * *", async () => {
        await mongo.client.connect()
        let collection = mongo.client.db("scout").collection("gloomdos")
        let bossdata = {}
        let end = false

        let cursor = await collection.find()
        await cursor.forEach((doc) => {
            if (doc["_id"]  == "[lastkillid]") {
                bossdata[doc["_id"]] = doc["data"]
            } else {
                bossdata[doc["_id"]] = {
                    "deaths" : doc["deaths"],
                    "dps" : doc["dps"],
                    "hps" : doc["hps"],
                    "mps" : doc["mps"],
                    "kills" : doc["kills"]
                }
            }
        })


        while (!end) {
            await axios.post(
                url = 'https://hordes.io/api/pve/getbosskillplayerlogs',
                data = JSON.stringify({
                    sort: "dps",
                    killid: bossdata["[lastkillid]"]
                })
            ).then(r => {
                if (!r.data.length && bossdata["[lastkillid]"] > 9000) {
                    end = true
                } else {
                    r.data.forEach(d => {
                        let time = d.time.split("T")[0]
                        let highest = Math.max(d.dps,d.hps,d.mps)
                        let mode = d.dps==highest ? "dps" : d.hps==highest ? "hps" : "mps"
                        let minscore = 100

                        if (highest > minscore) {
                            if (bossdata[d.name]) {
                                if (d[mode] > bossdata[d.name][mode]["record"][0] && d.duration >= 60) {
                                    bossdata[d.name][mode]["records"].push([d[mode], time])
                                    bossdata[d.name][mode]["record"] = [d[mode], time]
                                }
                                bossdata[d.name]["kills"].push([d.killid, time])
                                bossdata[d.name]["deaths"] += d.deaths
                            } else {
                                bossdata[d.name] = {
                                    "kills" : [[d.killid, time]],
                                    "deaths" : d.deaths,
                                    "dps" : {
                                        "record" :  [d.dps, time],
                                        "records" : [[d.dps, time]]
                                    },
                                    "hps" : {
                                        "record" :  [d.hps, time],
                                        "records" : [[d.hps, time]]
                                    },
                                    "mps" : {
                                        "record" :  [d.mps, time],
                                        "records" : [[d.mps, time]]
                                    }
                                }
                            }


                        }
                    })
                    bossdata["[lastkillid]"]++                
                }

            })
        }

        //fs.writeFile('bosskilldata.json', JSON.stringify(bossdata), 'utf8', function(){console.log("wrote file")});

        let bulkOp = []
        for (const item in bossdata) {
            try {
                var set = item=="[lastkillid]" ? { "data" : bossdata["[lastkillid]"]} : {
                    "kills" : bossdata[item]["kills"],
                    "deaths" : bossdata[item]["deaths"],
                    "dps" : bossdata[item].dps,
                    "hps" : bossdata[item].hps,
                    "mps" : bossdata[item].mps
                };
            }
            catch(err) {
                //console.log(item, err)
                var set = {}
            }
            bulkOp.push(
                {
                    updateOne : {
                        "filter" : {
                            "_id" : item
                        },
                        "update" : {
                            "$set" : set
                        },
                        "upsert" : true   
                    }
                }
            )
        }
        await collection.bulkWrite(bulkOp)
        await mongo.client.close();
        console.log("Updated gloom")
    });
  
    gloom.start();
  }
