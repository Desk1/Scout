<script>
export default {
	props: ["itemInfo"],
    data() {
        return {
            colours : {
                "Common" : "#DAE8EA",
                "Uncommon" : "rgb(52,203,73)",
                "Rare" : "rgb(6,129,234)",
                "Epic" : "rgb(158,59,249)",
                "Legendary" : "rgb(249,59,59)",
                "upgrade" : "#F5C247"
            },
            panelWidth: 230,
            panelHeight: 225
        }
    },
    methods: {
        getQuality(q) {
            if (q >= 99) {
                return "Legendary"
            }
            if (q >= 90) {
                return "Epic"
            }
            if (q >= 70) {
                return "Rare"
            }
            if (q >= 50) {
                return "Uncommon"
            }
            return "Common"
        },
        getDecimalPlace(n) {
            let num = String(n).split(".")
            if (!num[1]) {
                return 0
            }
            return num[1].length
        }
    },
    computed: {
        gridstyle() {
            let width = Math.ceil(Math.sqrt(this.itemInfo.length))
            return {
                'grid-template-columns' : `repeat(${width}, 1fr)`,
                'width' : `${(this.panelWidth * width) + 5 * (width-1) + 3 * (width * 2)}px`
                //'height' : `${(this.panelHeight * Math.ceil(this.itemInfo.length / width)) + 5 * (width-1) + 3 * (width * 2)}px`
            }
        },
        cssProps() {
            return {
                "--panelwidth" : `${this.panelWidth}px`,
                "--panelheight" : `${this.panelHeight}px`
            }
        }
    }
}
</script>

<template>
    <div id="itemgrid" :style="gridstyle">
        <div class="itempanel" v-for="item in itemInfo" :style="`border: 3px solid ${colours[getQuality(item.quality)]}`">
            <div style="padding: 8px">
                <div class="pack">
                    <div class="itemtitle" :style="`color: ${colours[getQuality(item.quality)]}`">
                        {{item.name}}
                        <span class="itemupgrade" :style="`color: ${colours['upgrade']}`">
                            +{{item.upgrade}}
                        </span>
                    </div>
                    <div class="itemtype" style="color: #DAE8EA">
                        {{getQuality(item.quality)}}
                        {{item.type.charAt(0).toUpperCase() + item.type.slice(1)}}
                        {{item.quality}}%
                    </div>
                    <small :style="`color: ${colours['Uncommon']}`">
                        GS: {{item.gearscore}}
                        <span class="itemid" style="color: #5b858e">
                            ID: {{item.ID}}
                        </span>
                    </small>
                </div>
                <div class="pack">
                    <div v-for="stat, k in item.attr" :style="`color: ${colours[getQuality(stat.quality)]}`">
                        <template v-if="!item.bonus_attr_keys.includes(k)">
                            {{stat.value.toFixed(getDecimalPlace(stat.attr_info["*"]))}}{{stat.attr_info["%"] ? "%" : ""}} 
                            {{stat.attr_info.long}}
                        </template>
                        <template v-else>
                            + {{stat.value.toFixed(getDecimalPlace(stat.attr_info["*"]))}}{{stat.attr_info["%"] ? "%" : ""}} {{stat.attr_info.long}} {{stat.quality}}%
                        </template>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style>
#itemgrid {
    display: grid;
    background-color: rgb(16,19,29);
    column-gap: 5px;
    row-gap: 5px;
    z-index: 100;
}

.itempanel {
    width: v-bind(panelWidth + "px");
    height: v-bind(panelHeight + "px");
    font-family: "hordes", sans-serif;
    letter-spacing: normal;
    line-height: normal;
    text-align: left;
}

.itemtitle {
    font-size: 20px;
    font-weight: bold;
    margin-top: 4px;
}

.pack {
    margin-block: 7px;
    font-size: 0.95rem;
}

</style>