class Settings {
    constructor() {
        this.currentSettings = this.retrieveStorage()
        this.refresh = false
        if (!this.currentSettings) {
            this.currentSettings = {
                "extensions" : {
                    "CC Indicator" : true,
                    "Revitalize Overlay" : false,
                    "Characterpanel" : true,
                    "Chat" : true,
                } 
            }

            this.updateStorage()
        }
    }

    getMutationCondition(mutation) {
        if (!mutation.addedNodes.length) {
            return false
        }

        return (
            mutation.target.className == "container svelte-k3qmu8" &&
            mutation.addedNodes[0].className == "container svelte-ntyx09"
        )
    }

    initialise(target) {
        this.settingsmenu = document.querySelector("body > div.l-ui.layout > div:nth-child(1) > div:nth-child(4) > div")
        this.insertHtml()
    }

    insertHtml() {
        let btn = document.createElement("div")
        btn.className = "choice "
        btn.textContent = "ScoutUI"
        btn.setAttribute("scout-key", "main")
        btn.addEventListener("click", () => {
            this.settingsmenu.querySelector(".active").classList.remove("active")
            btn.classList.add("active")
        })
        this.settingsmenu.querySelector("div.slot > div > div:nth-child(1)").appendChild(btn)

        this.settingsmenu.querySelector(".btn").addEventListener("click", () => {
            if (this.refresh) {
                location.reload()
            }
        })

        let defaultsettings = this.settingsmenu.querySelector(".menu")

        this.settingsmenu.querySelector(".divide").insertAdjacentHTML("beforeend", `
        <div data-panel="scout" class="menu scrollbar panel-black scoutsettings" style="display:none;">
            <h3 class="textprimary">Scout UI</h3>
            <div class="settings scoutmain">
            </div>
        </div>
        `)
        let scoutsettings = this.settingsmenu.querySelector(".scoutsettings .settings")
        scoutsettings.insertAdjacentHTML("beforeend", "<div class='textprimary'>Disabled mods</div><div></div>")

        for (const e in this.currentSettings.extensions) {
            scoutsettings.insertAdjacentHTML("beforeend", `<div>${e}</div>`)
            
            let modbtn = document.createElement("div")
            this.currentSettings.extensions[e] ? modbtn.className = "btn checkbox" : modbtn.className = "btn checkbox active"
            modbtn.addEventListener("click", () => {
                let value = modbtn.classList.contains("active")
                value ? modbtn.classList.remove("active") : modbtn.classList.add("active")
                this.currentSettings.extensions[e] = value
                this.updateStorage()
                this.refresh = true
            })
            scoutsettings.appendChild(modbtn)
        }


        const observation = (m) => {
            m.forEach(mutation => {
                if (mutation.target.className == "choice active") {
                    [...this.settingsmenu.querySelector(".divide").children].forEach(div => {
                        if (div.classList.contains("menu")) {
                            div.style.display = "none"
                        }
                    })

                    if (mutation.target.textContent == "ScoutUI") {
                        scoutsettings.parentElement.style.removeProperty("display")

                    } else {
                        if (mutation.target.getAttribute("data-key") == "default" || mutation.target.getAttribute("data-key") == null) {
                            defaultsettings.style.removeProperty("display")
                        } else {
                            this.settingsmenu.querySelector(`[data-panel=${mutation.target.getAttribute("data-key")}]`).style.removeProperty("display")
                        }
                        btn.classList.remove("active")
                    }
                }
            })
        }
        
        const observer = new MutationObserver(observation)
        observer.observe(this.settingsmenu, { attributes: true, childList: true, subtree: true })
    }

    insertHtml2() {
        let btn = document.createElement("div")
        btn.className = "choice "
        btn.textContent = "ScoutUI"
        setTimeout(() => {btn.setAttribute("data-key", "scout")})
        btn.addEventListener("click", () => {
            this.settingsmenu.querySelector(".active").classList.remove("active")
            btn.classList.add("active")
        })
        this.settingsmenu.querySelector("div.slot > div > div:nth-child(1)").appendChild(btn)

        this.settingsmenu.querySelector(".btn").addEventListener("click", () => {
            if (this.refresh) {
                location.reload()
            }
        })

        let defaultsettings = this.settingsmenu.querySelector(".settings")

        const observation = (m) => {
            m.forEach(mutation => {
                if (mutation.target.className == "choice active") {
                    this.settingsmenu.querySelector("h3").textContent = mutation.target.textContent

                    if (mutation.target.textContent == "ScoutUI" && !this.settingsmenu.querySelector(".scoutsettings")) {
                        defaultsettings.style.visibility = "hidden"
                        defaultsettings.style.position = "absolute"

                        let scoutsettings = document.createElement("div")
                        scoutsettings.className = "scoutsettings"
                        scoutsettings.insertAdjacentHTML("beforeend", "<div class='textprimary'>Disabled mods</div><div></div>")

                        for (const e in this.currentSettings.extensions) {
                            scoutsettings.insertAdjacentHTML("beforeend", `<div>${e}</div>`)
                            
                            let modbtn = document.createElement("div")
                            this.currentSettings.extensions[e] ? modbtn.className = "btn checkbox" : modbtn.className = "btn checkbox active"
                            modbtn.addEventListener("click", () => {
                                let value = modbtn.classList.contains("active")
                                value ? modbtn.classList.remove("active") : modbtn.classList.add("active")
                                this.currentSettings.extensions[e] = value
                                this.updateStorage()
                                this.refresh = true
                            })
                            scoutsettings.appendChild(modbtn)
                        }

                        this.settingsmenu.querySelector(".menu").appendChild(scoutsettings)

                    } else {
                        if (this.settingsmenu.querySelector(".scoutsettings")) {
                            this.settingsmenu.querySelector(".scoutsettings").remove()
                        }
                        defaultsettings.style.visibility = "visible"
                        defaultsettings.style.position = "inherit"
                        btn.classList.remove("active")
                    }

                    if (document.querySelector(".versiondiv") && mutation.target.textContent == "ScoutUI") {
                        [...this.settingsmenu.querySelector(".divide").children].forEach(div => {
                            if (div.classList.contains("menu")) {
                                div.style.display = "none"
                            }
                        })

                        this.settingsmenu.querySelector(".menu").style.removeProperty("display")
                    }
                }
            })
        }
        
        const observer = new MutationObserver(observation)
        observer.observe(this.settingsmenu, { attributes: true, childList: true, subtree: true })
    }

    getModSetting(mod) {
        return this.currentSettings.extensions[mod]
    }

    updateStorage() {
        localStorage.setItem("scout-settings", JSON.stringify(this.currentSettings))
    }

    retrieveStorage() {
        return JSON.parse(localStorage.getItem("scout-settings"))
    }
}
