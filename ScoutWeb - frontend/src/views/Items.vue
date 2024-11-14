<script>
import Item from "../components/Item.vue"
import decode from "../hordes/itemdecode.js"
import axios from "axios"

export default {
    components: {Item},
    data() {
        return {
            ids: [200203020,87715298,158513435,153487724],
            items: []
        }
    },
    mounted() {
        axios.post(`${this.$store.state.backend}/items`, { "ids": this.ids }).then(r => {
            this.items = r.data.map(i => decode(i, {maxupgrade: false}))
            console.log(this.items)
        })
    }
}
</script>

<template>
    <Item :itemInfo="items" />
</template>

<style>

</style>