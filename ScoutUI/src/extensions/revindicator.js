class revIndicator {
    getMutationCondition(mutation) {
        return (
            mutation.target.id == "expbar" &&
            extensions["Settings"].getModSetting("Revitalize Overlay")
        )
    }

    initialise(target) {
        let revButton = this.findRevButton()
        this.revQueue = undefined
        this.overlayQueue = "hidden"
        if (!revButton) { return }

        document.addEventListener("keydown", e => {
            if (e.key == revButton) {
                this.applyRevIndicator(revButton)
            }
        })

        const observation = (m) => {
            m.forEach(mutation => {
                if (this.revQueue && mutation.target.classList.contains("hidden") && this.overlayQueue == "queued") {
                    this.applyRevIndicator(revButton)
                    this.overlayQueue = "hidden"
                }
            })
        }

        const observer = new MutationObserver(observation)

        observer.observe(document.querySelector(`#sk${revButton} > div:nth-child(3)`), { attributes: true, childList: true, subtree: true })
    }

    findRevButton() {
        let found = false;
        [...document.querySelector("#skillbar").children].forEach(skill => {
            if (skill.querySelector("img").src == "https://hordes.io/data/ui/skills/7.avif?v=85711040") {
                found = skill.querySelector(".key").innerHTML
            }
        })

        return found
    }

    applyRevIndicator(revButton) {
        let target
        if (this.revQueue) {
            target = this.revQueue
        } else {
            target = document.querySelector(".target")
        }

        if (target) {
            if (!document.querySelector(`#sk${revButton} > div:nth-child(2)`).classList.contains("hidden")) { // rev on cooldown
                this.revQueue = document.querySelector(".target")
                this.overlayQueue = "queued"
                return
            }

            if (target.querySelector('.revOverlay')) {
                target.querySelector('.revOverlay').remove()
            }

            target.querySelector('div:nth-child(1)').insertAdjacentHTML('beforeend', '<div class="revOverlay"></div>')
            setTimeout(() => { target.querySelector('.revOverlay').style.width = "0%" }, 200)

            if (this.revQueue) {
                this.revQueue = undefined
            }
        }
    }
}
