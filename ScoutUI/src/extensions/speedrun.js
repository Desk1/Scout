class Speedrun {
    getMutationCondition(mutation) {
        return (
            mutation.target.id == "expbar"
        )
    }

    initialise(target) {
        if (!document.querySelector("#sctspeedrun")) {
            this.insertHtml(document.querySelector("body > div.l-ui.layout.svelte-1j9lddf > div:nth-child(1) > div.l-corner-ur.uiscaled"))
        }
        //this.active = false

        if (this.retrieveStorage()) {
            this.run = this.retrieveStorage()[this.getpname()]
            if (this.run) {
                this.playtimeStart = performance.now()
                this.activateSpeedrun()
            }
            //!run = this.initialiseStorage()
        }

        this.eligible = this.checkExp()
        if (!this.eligible) {
            document.querySelector("#sctspeedrun").remove()
        }
        console.log(this.eligible)
    }

    getpname() {
        return document.querySelector("#ufplayer > div.panel-black.bars.targetable.svelte-mohsod > div:nth-child(1) > div.progressBar.bghealth.svelte-i7i7g5 > span.left.svelte-i7i7g5").textContent
    }

    insertHtml(ur) {
        ur.querySelector("div").insertAdjacentHTML("afterbegin", `
        <div id="sctspeedrun" class="btn border black">
            <span>Speedrun<span>
        </div>
        `)
        ur.querySelector("#sctspeedrun").addEventListener("click", () => {
            if (document.querySelector(".speedrunmenu")) {
                return
            }
            document.querySelector(".container").insertAdjacentHTML("beforeend", `
            <div class="window panel-black speedrunmenu slot">
                <img src="/assets/ui/icons/cross.svg?v=5699699" class="btn black svgicon presetclose">
                <div class="titleframe textprimary" style="grid-column: span 2">Speedrun</div>
            </div>
            `)

            let menu = document.querySelector(".speedrunmenu")

            document.querySelector(".container .presetclose").addEventListener("click", () => {
                clearInterval(this.timer)
                menu.remove()
            })

            menu.insertAdjacentHTML("beforeend", `
                <span>Time</span>
                <span id="speedruntime" class="textprimary">00:00:00</span>
            `)

            //<div class="btn green speedrunactivate">Enable</div>
            if (!this.active) {
                if (this.eligible) {
                    let btn = document.createElement("div")
                    btn.className = "btn green speedrunactivate"
                    btn.textContent = "Activate"

                    btn.addEventListener("click", () => {
                        if (this.checkExp()) {
                            this.playtimeStart = performance.now()
                            this.initialiseStorage()
                            this.activateTimer()
                            this.activateSpeedrun()
                            btn.remove()
                        } else {
                            btn.remove()
                            menu.insertAdjacentHTML("beforeend", `
                            <span style="color: red; grid-column: span 2">Not eligible</span>
                            `)
                        }
                    })

                    menu.appendChild(btn)
                } else {
                    menu.insertAdjacentHTML("beforeend", `
                    <span style="color: red; grid-column: span 2">Not eligible</span>
                    `)
                }
            } else {
                this.activateTimer()
            }

        })
    }

    activateTimer() {
        let formatTime = (totalSeconds) => {
            let hours = Math.floor(totalSeconds / 3600);
            let minutes = Math.floor((totalSeconds - (hours * 3600)) / 60);
            let seconds = Math.floor(totalSeconds - (hours * 3600) - (minutes * 60));
            
            if (hours < 10) { hours = "0" + hours; }
            if (minutes < 10) { minutes = "0" + minutes; }
            if (seconds < 10) { seconds = "0" + seconds; }
            
            return `${hours}:${minutes}:${seconds}`;
        }

        this.timer = setInterval(() => {
            document.querySelector("#speedruntime").textContent = formatTime(this.run.time + ((performance.now() - this.playtimeStart) / 1000))
        }, 1000)
    }

    activateSpeedrun() {
        this.active = true
        document.querySelector("#sctspeedrun").className = "btn border green"

        const checkItems = (m) => {
            console.log(m)
            m.forEach(mutation => {
                //character panel
                if (mutation.target.className == "l-upperLeftModal container uiscaled svelte-ggsnc" && mutation.addedNodes.length) {
                    if (mutation.addedNodes[0].className == "window panel-black svelte-yjs4p5") {
                        console.log("char panel opened")
                    }
                }
                //inventory
                if (mutation.target.className == "l-corner-lr container svelte-1axz35n" && mutation.target.style.display != "none") {
                    
                }
            })
        }
        const observer = new MutationObserver(checkItems)
        observer.observe(document.querySelector(".container"), { attributes: true, childList: true, subtree: true })

        //force open char panel / inv
        document.body.dispatchEvent(new KeyboardEvent('keydown', {
            bubbles: true,
            cancelable: false,
            key: "c"
        }));

        setTimeout(() => {
            if (!document.querySelector("body > div.l-ui.layout.svelte-1j9lddf > div:nth-child(1) > div.l-upperLeftModal.container.uiscaled.svelte-ggsnc > div")) {
                localStorage.setItem("kbCharacter", '"c"')
                location.reload()
            }
        })

        setInterval(() => {
            this.updateStorage()
        }, 500);
    }

    checkExp() {
        let check = false
        //exp
        let currentExp = document.querySelector("#expbar > div > div.progressBar.bgexp.svelte-i7i7g5 > span.left.svelte-i7i7g5").textContent.split(" ")
        currentExp = [parseInt(currentExp[0]), parseInt(currentExp[2])]
        if (!this.run) {
            return (currentExp[0] == 0 && currentExp[1] == 30)
        } else {
            return (currentExp[0] == this.run.exp[0] && currentExp[1] == this.run.exp[1])
        }

        /*
        let itemscheck = true
        //equipped items
        if (!document.querySelector("#equipslots")) {
            document.body.dispatchEvent(new KeyboardEvent('keydown', {
                bubbles: true,
                cancelable: false,
                key: "c"
            }));
        };
        setTimeout(() => {
            [...document.querySelector("#equipslots").children].forEach(slot => {
                if (slot.classList.contains("filled")) {
                    itemscheck = false
                }
            })

            //inventory items
            if (!"body > div.l-ui.layout.svelte-1j9lddf > div:nth-child(1) > div.l-corner-lr.container.svelte-1axz35n > div > div.slot.svelte-yjs4p5 > div.slotcontainer.svelte-1axz35n") {
                document.body.dispatchEvent(new KeyboardEvent('keydown', {
                    bubbles: true,
                    cancelable: false,
                    key: "b"
                }));
            }
            setTimeout(() => {
                [...document.querySelector("body > div.l-ui.layout.svelte-1j9lddf > div:nth-child(1) > div.l-corner-lr.container.svelte-1axz35n > div > div.slot.svelte-yjs4p5 > div.slotcontainer.svelte-1axz35n").children].forEach((slot, index) => {
                    if (index == 0) {
                        if (slot.classList.contains("filled")) {
                            if (slot.querySelector("img").src != "https://hordes.io/assets/items/misc/misc0_q0.webp?v=5699699" && slot.querySelector("span").textContent != "5") {
                                itemscheck = false
                            }
                        }
                    } else if (index == 1) {
                        if (slot.classList.contains("filled")) {
                            if (slot.querySelector("img").src != "https://hordes.io/assets/items/misc/misc1_q0.webp?v=5699699" && slot.querySelector("span").textContent != "5") {
                                itemscheck = false
                            }
                        }
                    } else {
                        if (slot.classList.contains("filled")) {
                            itemscheck = false
                        }
                    }
                })

                console.log("exp", expcheck)
                console.log("items", itemscheck)

                return true
            }, 500)
        }, 500)
        */
    }

    updateEligible() {
        let check = false
    }

    initialiseStorage() {
        this.run = {
            time: 0,
            exp: [0,30]
        }
        let store = this.retrieveStorage()
        if (!store) {
            store = {
                [this.getpname()] : this.run
            }
        } else {
            store[this.getpname()] = this.run
        }
          
        localStorage.setItem("scout-speedrun", JSON.stringify(store))

        return store[this.getpname()]
    }
    
    retrieveStorage() {
        return JSON.parse(localStorage.getItem("scout-speedrun"))
    }

    updateStorage() {
        let store = this.retrieveStorage()
        let currentExp = document.querySelector("#expbar > div > div.progressBar.bgexp.svelte-i7i7g5 > span.left.svelte-i7i7g5").textContent.split(" ")
        currentExp = [parseInt(currentExp[0]), parseInt(currentExp[2])]

        store[this.getpname()].time = Math.floor(this.run.time + ((performance.now() - this.playtimeStart) / 1000))
        store[this.getpname()].exp = currentExp

        localStorage.setItem("scout-speedrun", JSON.stringify(store))
    }

}