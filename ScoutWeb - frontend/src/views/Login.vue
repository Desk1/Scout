<script>
import axios from "axios";

export default {
    mounted() {
        /*
        axios.get(
            "https://discord.com/api/users/@me",
            { headers : {"Authorization" : `Bearer ${this.$route.query.token}`} }
        )
        .then(r => {
            this.$store.commit("login", r.data)
        })
        */

        this.$router.push({name:"home"})
    }
}
</script>


<style>
</style>