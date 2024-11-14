var express = require("express");
var app = express();
var axios = require('axios')
const scheduledFunctions = require('./jobs');
var qs = require('qs')
var { MongoClient } = require("mongodb");
var Long = require('mongodb').Long;

var dev = false

if (!dev) {
    scheduledFunctions.initScheduledJobs()
}
const discord = {
    CLIENT_ID : "",
    SECRET : ""
}

const mongo = {
    client : new MongoClient("")
}

const tierlist = {
    1 : "1kdIgCeDl6kl5wwsOCg0HO-9KzWLO2tHUZUvfKwjU52s", // Mage
    2 : "1z7JHoIZdOPrj_VYSGLxoJVw1RA1Nfptj8AClcUXc6O0", // Archer
    3 : "1aD_Zf-L9F8-NncMQa6C671EaoXgtEWnWDU1xATWlhgw",  // Shaman
    0 : "150QNvGaKPkOQ6pKD1z2SPWfXjjYS0p7RrH8LMRWFIC8" // Warrior
}


app.use((req, res, next) => {
    res.append('Access-Control-Allow-Origin', `${dev ? "*" : 'https://scoutbot.net'}`);
    res.append('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE');
    res.append('Access-Control-Allow-Headers', 'Content-Type');
    next();
});
app.use(express.json());

app.get("/players", (req, res) => {
    if (!req.query.player) {
        return res.send("Error")
    }
    var data = {name : req.query.player, order : "gs", limit : 25, offset : 0}
    axios.post('https://hordes.io/api/playerinfo/search', data, )
    .then(r => {
        var found = false
        r.data.forEach(p => {
            if (p.name.toLowerCase() == req.query.player.toLowerCase()) {
                found = true
                return res.json(p)
            }
        })
        if (!found) {
            res.send("Not found")
        }
    }).catch(() => {
        res.send("Error")
    })
});

app.post("/items", (req, res) => {
    try {
        axios.post(
            url = 'https://hordes.io/api/item/get',
            data = JSON.stringify(req.body),
            config = {
                headers: {
                    Cookie: ""
                }
            }
        ).then(r => {
            return res.json(r.data)
        })    
    }
    catch(err) {
        res.send("Error")
    }
})

app.get("/characters", async (req, res) => {
    try {
        if (!req.query.userid) {
            return res.send("Error")
        }
    
        await mongo.client.db("scout").collection("characters").findOne({'_id':Long.fromString(req.query.userid)})
        .then(d => {
            if (d) {
                res.json(d.characters)
            } else {
                res.json([])
            }
        })
    }
    catch(err) {
        res.send("Error")
    }
});

app.get("/gloom", async function(req, res) {
    if (!req.query.player) {
        return res.send("Error")
    }
    
    await mongo.client.db("scout").collection("gloomdos").findOne({"_id" : req.query.player})
    .then(doc => {
        res.json(doc)
    })
});

app.get("/tierlist", (req, res) => {
    if (!req.query.pclass) {
        res.send("Error")
    } else if (req.query.items == "true" && req.query.name) {
        let url = `https://sheets.googleapis.com/v4/spreadsheets/${tierlist[req.query.pclass]}/values:batchGet?ranges=data!A2:O1000&majorDimension=COLUMNS&key=${SPREADSHEET_KEY}`
        axios.get(url).then(r => {
            let data = r.data["valueRanges"][0]["values"]
            switch (req.query.pclass) {
                case "1":
                    var gearloc = 4
                    break
                case "2":
                    var gearloc = 4
                    break
                case "3":
                    var gearloc = 6
                    break
                case "0":
                    var gearloc = 14
                    break
            }
            
            let loc = data[0].map(x => x.toLowerCase()).indexOf(req.query.name)
            let guh = data[gearloc][loc]
            if (guh) {
                let gear = guh.split(",").map(Number)
                res.json(gear)
            } else {
                res.json([])
            }
        
        })
    } else {
        let range = (req.query.pclass == "0") ? "AG6:AH21" : "X6:Y21"
        let dimension = "ROWS"
        let url = `https://sheets.googleapis.com/v4/spreadsheets/${tierlist[req.query.pclass]}/values:batchGet?ranges=data!${range}&majorDimension=${dimension}&key=${SPREADSHEET_KEY}`
        let result = {}

        axios.get(url).then(r => {
            result.boundaries = r.data["valueRanges"][0]["values"].reverse()

            range = (req.query.pclass == "0") ? "AD2:AD" : "U2:U"
            dimension = "COLUMNS"
            url = `https://sheets.googleapis.com/v4/spreadsheets/${tierlist[req.query.pclass]}/values:batchGet?ranges=data!${range}&majorDimension=${dimension}&key=${SPREADSHEET_KEY}`

            axios.get(url).then(r => {
                result.rankings = r.data["valueRanges"][0]["values"][0]
                res.json(result)
            })

        })
    }
    


});

app.get("/names", function(req, res) {
    axios.all([
        axios.get(`https://sheets.googleapis.com/v4/spreadsheets/1kdIgCeDl6kl5wwsOCg0HO-9KzWLO2tHUZUvfKwjU52s/values:batchGet?ranges=data!A2:A&majorDimension=COLUMNS&key=${SPREADSHEET_KEY}`),
        axios.get(`https://sheets.googleapis.com/v4/spreadsheets/1z7JHoIZdOPrj_VYSGLxoJVw1RA1Nfptj8AClcUXc6O0/values:batchGet?ranges=data!A2:A&majorDimension=COLUMNS&key=${SPREADSHEET_KEY}`),
        axios.get(`https://sheets.googleapis.com/v4/spreadsheets/1aD_Zf-L9F8-NncMQa6C671EaoXgtEWnWDU1xATWlhgw/values:batchGet?ranges=data!A2:A&majorDimension=COLUMNS&key=${SPREADSHEET_KEY}`),
        axios.get(`https://sheets.googleapis.com/v4/spreadsheets/150QNvGaKPkOQ6pKD1z2SPWfXjjYS0p7RrH8LMRWFIC8/values:batchGet?ranges=data!A2:A&majorDimension=COLUMNS&key=${SPREADSHEET_KEY}`)
    ])
    .then(axios.spread((o1, o2, o3, o4) => {
        let arr = []
        res.json(arr.concat(
            o1.data["valueRanges"][0]["values"][0],
            o2.data["valueRanges"][0]["values"][0],
            o3.data["valueRanges"][0]["values"][0],
            o4.data["valueRanges"][0]["values"][0]
        ))
    }))
})

app.get("/pvp", function(req, res) {
    axios.get("https://hordes.io/api/pvp/getfactionpercentiles")
    .then(r => {
        res.json(r.data)
    })
})

app.get("/loginredirect", async function(req, res) {
    var code = req.query.code;

    var body = {
        'client_id': discord.CLIENT_ID,
        'client_secret': discord.SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': dev ? 'http://localhost:3001/loginredirect' : 'https://pear-funny-drill.cyclic.app/loginredirect'
    };

    axios.post(
        url="https://discord.com/api/v10/oauth2/token",
        data=qs.stringify(body),
        config = {
            headers: {'Content-Type': 'application/x-www-form-urlencoded'}
        }
    )
    .then(r => {
        var re = dev ? `http://localhost:3000?token=${r.data.access_token}` : `http://scoutbot.net?token=${r.data.access_token}`
        res.redirect(re)
    })
    .catch(() => {
        console.log("login error")
    })
    
});


// error handler middleware
/*
app.use((error, req, res, next) => {
    res.status(error.status || 500).send({
        error: {
            status: error.status || 500,
            message: error.message || 'Internal Server Error',
        },
    });
});
*/

var port = dev ? 3001 : 3000
app.listen(process.env.PORT || port, async () => {
    await mongo.client.connect()
    console.log(`Server running on port ${port}`);
});
