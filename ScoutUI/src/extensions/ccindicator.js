class CCIndicator {
    constructor() {
        this.hardCC = [
            "https://hordes.io/data/ui/skills/37.avif?v=85711040", //  agonize
            "https://hordes.io/data/ui/skills/50.avif?v=85711040", // relentless
            "https://hordes.io/data/ui/skills/49.avif?v=85711040", // blind shot
            "https://hordes.io/data/ui/skills/deepFrozen.avif?v=85711040", // deep freeze
            "https://hordes.io/data/ui/skills/stunBuff.avif?v=85711040", // charge
            "https://hordes.io/data/ui/skills/28.avif?v=85711040" //test canine
        ]
        this.medCC = [
            "https://hordes.io/data/ui/skills/14.avif?v=85711040", // chilling
            "https://hordes.io/data/ui/skills/7.avif?v=85711040" //test rev
        ]
    }

    getMutationCondition(mutation) {
        return (
            mutation.target.className == "buffarray party svelte-g292qg" &&
            (mutation.addedNodes.length || mutation.removedNodes.length) &&
            extensions["Settings"].getModSetting("CC Indicator")
        )
    }

    initialise(target) {
        // init cc overlay if not exisisting
        let overlay = target.parentElement.parentElement.querySelector(".ccOverlay")
        if (!overlay) {
            overlay = this.initCCIndicator(target.parentElement.parentElement)
            target.parentElement.parentElement.appendChild(overlay)
        }

        //guh
        overlay.style.setProperty("--cctransition", "background 1s ease-out")

        //determine level
        let cclevel = "noCC";
        for (const e of [...target.children]) {
            if (this.hardCC.includes(e.querySelector('img').src)) {
                cclevel = "hardCC"
                break
            }

            if (this.medCC.includes(e.querySelector('img').src)) {
                cclevel = "mediumCC"
            }
        }

        this.setCCLevel(overlay, cclevel)

        //this.applyCCIndicator(target.parentElement.parentElement, cclevel)
    }

    setCCLevel(overlay, level) {
        /*overlay.classList.remove("noCC")
        overlay.classList.remove("mediumCC")
        overlay.classList.remove("hardCC")
        */

        switch (level) {
            case "hardCC":
                overlay.style.setProperty("--shadow", "0px 0px 0px 3px #fc0328")
                overlay.style.setProperty("--bg", "rgba(252, 40, 40, 0.8)")
                break

            case "mediumCC":
                overlay.style.setProperty("--shadow", "0px 0px 0px 3px #fcce03")
                overlay.style.setProperty("--bg", "rgba(255, 227, 47, 0.52)")
                break

            case "noCC":
                overlay.style.setProperty("--shadow", "none")
                overlay.style.setProperty("--bg", "none")
                break
        }

        setTimeout(() => {
            overlay.style.setProperty("--bg", "none")
            //overlay.style.setProperty("--cctransition", "none")
        })
    }

    initCCIndicator(target) {
        let overlay = document.createElement("div")
        overlay.classList.add("ccOverlay")
        overlay.classList.add("panel-black")
        let dimensions = target.querySelector(".panel-black").getBoundingClientRect()
        overlay.style.width = dimensions.width + "px"
        overlay.style.height = dimensions.height + "px"
        //if not ruin
        if (!document.querySelector(".versiondiv")) {
            overlay.style.left = target.querySelector(".iconcontainer").getBoundingClientRect().width + 4 + "px"
        }

        return overlay
    }

    applyCCIndicator(target, level) {
        var overlay = target.querySelector('.ccOverlay')
        if (overlay) {
            if (overlay.classList.contains(level)) {
                return
            }
            overlay.remove()
        }

        overlay = document.createElement("div")
        overlay.classList.add("ccOverlay")
        overlay.classList.add(level)
        overlay.classList.add("panel-black")
        let dimensions = target.querySelector(".panel-black").getBoundingClientRect()
        overlay.style.width = dimensions.width + "px"
        overlay.style.height = dimensions.height + "px"
        //if not ruin
        if (!document.querySelector(".versiondiv")) {
            overlay.style.left = target.querySelector(".iconcontainer").getBoundingClientRect().width + 4 + "px"
        }

        target.appendChild(overlay)
        setTimeout(() => {target.querySelector('.ccOverlay').style.background = "none"})
    }
}
