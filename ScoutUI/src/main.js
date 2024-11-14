const ExtensionList = [Settings, Chat, CharacterPanel, CCIndicator, revIndicator, skillPresets]
var extensions = {}
const version = "0.2"


ExtensionList.forEach(e => {
    let extension = new e
    extensions[extension.constructor.name] = extension
})

const observation = (m) => {
    m.forEach(mutation => {
        for (const e in extensions) {
            if (extensions[e].getMutationCondition(mutation)) {
                extensions[e].initialise(mutation.target)
            }
        }
    })
}

const observer = new MutationObserver(observation)

observer.observe(document.body, { attributes: true, childList: true, subtree: true })