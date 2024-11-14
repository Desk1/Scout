class Chat {
    getMutationCondition(mutation) { 
        return (
            mutation.target.id == "chatinput" &&
            mutation.previousSibling == null &&
            extensions["Settings"].getModSetting("Chat")
        )
        
    }

    initialise(target) {
        let chatstate = this.retrieveStorage()
        
        if (chatstate) {
            let chat = document.querySelector("#chat").parentElement
            let timeout = 0

            if (document.querySelector(".versiondiv")) {
                timeout = 1250
            }

            setTimeout(() => {
                chat.style.width = chatstate.width
                chat.style.height = chatstate.height
                chat.style.left = chatstate.left
                chat.style.bottom = chatstate.bottom
            }, timeout)
        }

        this.styleChat()

        if (!document.querySelector("#resizer")) { this.addResizer() }

        if (!document.querySelector("#positioner")) { this.addPositioner() }

        this.addSystemMsg(`ScoutUI ${version}`, "afterbegin")
    }

    styleChat() {
        let chatBox = document.querySelector("#chat")

        chatBox.style.setProperty("--linewrapbg", "transparant")
        chatBox.style.setProperty("--linewrapshadow", "none")
        chatBox.style.setProperty("--channelbg", "transparant")
        chatBox.style.setProperty("--chatbg", "#050606c2")
    }

    addResizer() {
        var chat = document.querySelector("#chat").parentElement
        var resizer = document.createElement('div');
        resizer.id = 'resizer';
        resizer.classList.add("chatTransformer")
        document.querySelector("#chat").before(resizer);

        resizer.addEventListener('mousedown', initDrag, false);

        var startX, startY, startWidth, startHeight;

        function initDrag(e) {
            startX = e.clientX;
            startY = e.clientY;
            startWidth = parseInt(document.defaultView.getComputedStyle(chat).width, 10);
            startHeight = parseInt(document.defaultView.getComputedStyle(chat).height, 10);

            document.documentElement.addEventListener('mousemove', doDrag, false);
            document.documentElement.addEventListener('mouseup', stopDrag, false);
        }

        function doDrag(e) {
            chat.style.width = (startWidth + e.clientX - startX) + 'px';
            chat.style.height = (startHeight - e.clientY + startY) + 'px';
        }

        const stopDrag = (e) => {
            document.documentElement.removeEventListener('mousemove', doDrag, false);
            document.documentElement.removeEventListener('mouseup', stopDrag, false);

            this.updateStorage()
        }
    }

    addPositioner() {
        var chat = document.querySelector("#chat").parentElement
        var positioner = document.createElement('div');
        positioner.id = 'positioner';
        positioner.classList.add("chatTransformer")
        document.querySelector("#chat").before(positioner);

        positioner.addEventListener('mousedown', initDrag, false);

        var startX, startY, startLeft, startBottom;


        function initDrag(e) {
            startX = e.clientX;
            startY = e.clientY;
            startLeft = parseInt(document.defaultView.getComputedStyle(chat).left, 10);
            startBottom = parseInt(document.defaultView.getComputedStyle(chat).bottom, 10);

            document.documentElement.addEventListener('mousemove', doDrag, false);
            document.documentElement.addEventListener('mouseup', stopDrag, false);
        }

        function doDrag(e) {
            chat.style.left = startLeft + (e.clientX - startX) + 'px';
            chat.style.bottom = startBottom - (e.clientY - startY) + 'px';
        }

        const stopDrag = (e) => {
            document.documentElement.removeEventListener('mousemove', doDrag, false);
            document.documentElement.removeEventListener('mouseup', stopDrag, false);

            this.updateStorage()
        }
    }

    addSystemMsg(msg, location="beforeend") {
        document.querySelector("#chat").insertAdjacentHTML(location, `
        <article class="line svelte-16y0b84">
        <div class="linewrap svelte-16y0b84">
            <span class="time svelte-16y0b84">xx.xx</span>
            <span class="textGM textScout svelte-16y0b84">${msg}</span>
        </div>
        </article>
        `)
    }

    updateStorage() {
        let chat = document.querySelector("#chat").parentElement

        let settings = {
            "height" : chat.style.height,
            "width" : chat.style.width,
            "left" : chat.style.left,
            "bottom" : chat.style.bottom
        }

        localStorage.setItem("scout-chatsettings", JSON.stringify(settings))
    }

    retrieveStorage() {
        return JSON.parse(localStorage.getItem("scout-chatsettings"))
    }
}
