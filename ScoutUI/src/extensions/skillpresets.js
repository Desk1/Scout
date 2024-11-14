class skillPresets {
    getMutationCondition(mutation) {
        return (
            mutation.target.className == "l-upperLeftModal container svelte-urqsjg" &&
            mutation.previousSibling == null
        )
    }

    initialise() {
        this.changing = false
        this.pclass = this.getpclass()
        let store = this.retrieveStorage()
        if (!store) {
            this.presets = []
        } else {
            if (!store[this.pclass]) {
                this.presets = []
            } else {
                this.presets = this.retrieveStorage()[this.pclass]
            }
        }

        if (!document.querySelector(".presetmenu")) {
            this.insertHtml()
        }
    }

    getpclass() {
        let icons = this.getSkillIcons()

        //this is dumb but idk
        if (icons.includes("https://hordes.io/assets/ui/skills/6.webp?v=5699699")) {
            return "shaman"
        } else if (icons.includes("https://hordes.io/assets/ui/skills/1.webp?v=5699699")) {
            return "warrior"
        } else if (icons.includes("https://hordes.io/assets/ui/skills/9.webp?v=5699699")) {
            return "archer"
        } else if (icons.includes("https://hordes.io/assets/ui/skills/4.webp?v=5699699")) {
            return "mage"
        }
    }

    insertHtml() {
        let skillpanel = document.querySelector("body > div.l-ui.layout > div:nth-child(1) > div.l-upperLeftModal.container > div")
        let titleframe = skillpanel.querySelector(".titleframe")
        let slot = skillpanel.querySelector(".slot")

        skillpanel.style.gridTemplateColumns = "1fr auto"
        skillpanel.style.gridTemplateRows = "none"

        let skillmenu = document.createElement("div")
        skillmenu.className = "skillmenu"

        let presetmenu = document.createElement("div")
        presetmenu.className = "presetmenu panel-black bar"

        skillpanel.replaceChild(skillmenu, titleframe)
        skillpanel.replaceChild(presetmenu, slot)

        skillmenu.appendChild(titleframe)
        skillmenu.appendChild(slot)

        //if ruin
        if (document.querySelector(".versiondiv")) {
            presetmenu.style.gridTemplateRows = "53px auto"
        }


        presetmenu.innerHTML = `
        <div class="presettitle">
        <span class="textprimary">Presets</span>
        <div class="presetbuttons">
            <div class="btn grey" id="presetimport">Import</div>
            <div class="btn grey" id="presetexport">Export</div>
            <div class="btn grey disabled" id="presetdelete">Delete</div>
        </div>
        </div>
        <div class="presetlist"></div>
        `

        presetmenu.querySelector("#presetimport").addEventListener("click", () => {
            if (!document.querySelector(".presetimportmenu")) {
                document.querySelector(".container").insertAdjacentHTML("beforeend", `
                <div class="window panel-black presetimportmenu slot">
                    <img src="/assets/ui/icons/cross.svg?v=5699699" class="btn black svgicon presetclose">
                    <div class="titleframe textprimary" style="grid-column: span 2">Import Presets</div>
                    <input type="text" style="grid-column: span 2">
                    <div class="btn grey presetimportbtn" style="grid-column: span 2">Add</div>
                </div>
                `)

                document.querySelector(".presetimportbtn").addEventListener("click", () => {
                    this.importPresets(document.querySelector(".presetimportmenu input").value)
                })

                document.querySelector(".presetimportmenu .presetclose").addEventListener("click", () => {
                    document.querySelector(".presetimportmenu").remove()
                })
            }
            
        })

        presetmenu.querySelector("#presetexport").addEventListener("click", () => {
            let encoded = btoa(JSON.stringify({
                data: this.presets,
                pclass: this.pclass
            }))
            let chat = document.querySelector("#chat")

            navigator.clipboard.writeText(encoded).then(function() {
                extensions["Chat"].addSystemMsg("Skill presets copied to clipboard")
            }, function(err) {
                extensions["Chat"].addSystemMsg("Failed to export skill presets")
            });
        })

        presetmenu.querySelector("#presetdelete").addEventListener("click", () => {
            let boxselected = presetmenu.querySelector(".selected")

            if (boxselected) {
                this.presets.splice([...presetmenu.querySelector(".presetlist").children].indexOf(boxselected), 1)

                this.insertPresets()
            }
        })

        this.insertPresets()
    }

    insertPresets() {
        let presetlist = document.querySelector(".presetlist")

        while (presetlist.firstChild) {
            presetlist.removeChild(presetlist.firstChild);
        }

        this.presets.forEach(preset => {
            let panel = document.createElement("div")
            panel.className = "panel-bright presetbox"
            panel.innerHTML = `
            <div id="" class="border white  slot filled svelte-18ojcpo">
                <img class="icon slotskill svelte-18ojcpo">
            </div>
            <div>
                <div class="textprimary textcenter name"></div>
            </div>
            <div>
                <div class="btn presetchoose grey"></div>
            </div>
            `
            panel.querySelector(".name").textContent = preset.name
            panel.querySelector("img").src = preset.icon 
            
            presetlist.appendChild(panel)
        });

        if (this.presets.length < 8) {
            presetlist.innerHTML += `
            <div class="btn grey" id="presetadd">Add new preset</div>
            `

            presetlist.querySelector("#presetadd").addEventListener("click", () => {
                if (!document.querySelector(".presetaddmenu")) {
                    this.addPreset()
                }
            })
        };
        
        [...presetlist.children].forEach((preset,index) => {
            if (preset.classList.contains("presetbox")) {
                preset.querySelector(".presetchoose").addEventListener("click", (e) => {
                    e.stopPropagation()
                    if (!this.changing) {
                        if (presetlist.querySelector(".green")) {
                            presetlist.querySelector(".green").className = "btn presetchoose grey"
                        }
                        preset.querySelector(".presetchoose").className = "btn presetchoose green"

                        preset.insertAdjacentHTML("beforeend", "<div class='presetoverlay'></div>")
                        setTimeout(() => {
                            let overlay = preset.querySelector(".presetoverlay")
                            overlay.style.width = "100%"
                            setTimeout(() => {
                                overlay.style.opacity = "0%"
                                setTimeout(() => {
                                    overlay.remove()
                                }, 200)
                            }, 1500)
                            
                        })

                        this.selectPreset(index)
                    }
                })
                preset.addEventListener("click", () => {
                    if (presetlist.querySelector(".selected")) {
                        presetlist.querySelector(".selected").classList.remove("selected")
                    }
                    preset.classList.add("selected")

                    document.querySelector("#presetdelete").classList.remove("disabled")
                })
            }
        })

        this.updateStorage()
    }

    selectPreset(index) {
        if (this.changing) {
            return
        }
        
        this.changing = true
        this.removeCurrentSkills()
        setTimeout(() => {
            let skilllist = document.querySelector("#skilllist");
            let skillset = this.presets[index].data;

            [...skilllist.children].forEach((skill, idx) => {
                if (skill.querySelector(".skillpoints")) {
                    for (let i=0; i<skillset[idx]; i++) {
                        skill.querySelector("div:nth-child(3) > .skillpoints > div:nth-child(2)").click()
                    }
                }
            })

            skilllist.parentElement.querySelector("#tutapplyskills").click()
            this.changing = false
        }, 1500)
    }

    addPreset() {
        let icons = this.getSkillIcons()

        document.querySelector(".container").insertAdjacentHTML("beforeend", `
        <div class="window panel-black presetaddmenu slot">
            <img src="/assets/ui/icons/cross.svg?v=5699699" class="btn black svgicon presetclose">
            <div class="titleframe textprimary" style="grid-column: span 2">Add Preset</div>
            <span>Name</span>
            <input type="text">
            <span>Icon</span>
            <div class="preseticongrid">
            </div>
            <div class="btn grey presetaddbtn" style="grid-column: span 2">Add</div>
        </div>
        `)
        let menu = document.querySelector(".presetaddmenu")

        menu.querySelector(".presetclose").addEventListener("click", () => {
            menu.remove()
        })

        icons.forEach(imgsrc => {
            let icon = document.createElement("div")
            icon.className = "border white slot filled svelte-18ojcpo"
            icon.innerHTML = `<img class="icon slotskill svelte-18ojcpo" src="${imgsrc}">`

            icon.addEventListener("click", () => {
                if (menu.querySelector(".green")) {
                    menu.querySelector(".green").className = "border white slot filled svelte-18ojcpo"
                }

                icon.className = "border green slot filled svelte-18ojcpo"
            })
            menu.querySelector(".preseticongrid").appendChild(icon)
        })

        menu.querySelector(".presetaddbtn").addEventListener("click", () => {
            let presetname = menu.querySelector("input").value
            let preseticon = menu.querySelector(".green")

            if (presetname && preseticon) {
                this.presets.push({
                    name: presetname,
                    icon: preseticon.querySelector("img").src,
                    data: this.getCurrentSkills()
                })

                this.insertPresets()

                menu.remove()
            }
        })
    }

    importPresets(encoded) {
        let decoded = JSON.parse(atob(encoded))
        let chat = document.querySelector("#chat")

        if (decoded.pclass != this.pclass) {
            chat.insertAdjacentHTML("beforeend", `
                <article class="line svelte-16y0b84">
                <div class="linewrap svelte-16y0b84">
                    <span class="time svelte-16y0b84">21.57</span>
                    <span class="textGM textScout svelte-16y0b84">Error importing skill presets: incorrect class</span>
                </div>
                </article>
            `)
            return
        }

        this.presets = decoded.data
        this.insertPresets()

        chat.insertAdjacentHTML("beforeend", `
            <article class="line svelte-16y0b84">
            <div class="linewrap svelte-16y0b84">
                <span class="time svelte-16y0b84">21.57</span>
                <span class="textGM textScout svelte-16y0b84">Skill presets successfully imported</span>
            </div>
            </article>
        `)
    }

    getSkillIcons() {
        let icons = [];

        [...document.querySelector("#skilllist").children].forEach(skill => {
            icons.push(skill.querySelector("img").src)
        })

        return icons
    }

    getCurrentSkills() {
        let skilllist = document.querySelector("#skilllist");
        let skills = [];

        [...skilllist.children].forEach(skill => {
            if (skill.querySelector(".skillpoints")) {
                skills.push(parseInt(skill.querySelector("div:nth-child(3) > .name").textContent.charAt(4)))
            } else {
                skills.push(0)
            }
        })

        return skills
    }

    removeCurrentSkills() {
        let skilllist = document.querySelector("#skilllist");
        let currentSkills = this.getCurrentSkills();

        [...skilllist.children].forEach((skill, index) => {
            if (skill.querySelector(".skillpoints")) {
                for (let i=0; i<currentSkills[index]; i++) {
                    skill.querySelector("div:nth-child(3) > .skillpoints > div:nth-child(1)").click()
                }
            }
        })
    }

    updateStorage() {
        let store = this.retrieveStorage()

        if (!store) {
            store = {}
        }
        store[this.pclass] = this.presets
          
        localStorage.setItem("scout-skillpresets", JSON.stringify(store))
    }

    retrieveStorage() {
        return JSON.parse(localStorage.getItem("scout-skillpresets"))
    }
}
