<script>
import { LMap, LCircle, LMarker, LTileLayer } from '@vue-leaflet/vue-leaflet';

export default {
  components: {
    LMap,
    LCircle,
    LMarker,
    LTileLayer,
  },
  data() {
    return {
      colours: {
        "circle": "#b2182b"
      },
      circle: {
        radius: 2500
      },
      map: {
        zoom: 13,
        bounds: null,
        url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attribution: '&copy; <a target="_blank" href="http://osm.org/copyright">OpenStreetMap</a> contributors'
      },
      user_inputs: {
        nroutes: 1,
        distance: 1000,
        lat: 0,
        lng: 0,
      },
    }
  },
  async created() {

    // get user's coordinates from browser request
    // this.$getLocation({})
    //   .then(coordinates => {
    //     this.myCoordinates = coordinates;
    //   })
    //   .catch(error => alert(error));

    //   navigator.geolocation.getCurrentPosition({})
    //     .then(coords => {
    //       this.coords = coords;
    //     })
    //     .catch(error => alert(error))
    // 

    navigator.geolocation.getCurrentPosition(
      position => {
        console.log("Read location from HTML5's gelocation")
        console.log([position.coords.latitude, position.coords.latitude])
        this.user_inputs.lat = position.coords.latitude;
        this.user_inputs.lng= position.coords.longitude;
      },
      error => {
        console.log(error.message);
        alert("Please refresh running-routes and share your location")
      }
    )
  },
  methods: {
    updateBounds(value) {
      this.$nextTick(() => {
        this.$refs.myMap.leafletObject.flyToBounds(
          this.$refs.outsideCircle.leafletObject.getBounds()
        )
      })
    }
    }
  }
</script>

<template>
  <header>
    <div>
      <h1>Running routes</h1>
      <hr />
      <h2>I want to run</h2>
      <select v-model="user_inputs.distance" @change="updateBounds">
        <option>1000</option>
        <option>2000</option>
        <option>3000</option>
        <option>4000</option>
        <option>5000</option>
      </select>
      <h2>meters.</h2>
      <br />
      <span>inputs: {{ user_inputs.distance }}, {{ user_inputs.distance / 2 }}</span>
      <br />
      <button>Generate</button>
      <br />
      <p>{{ user_inputs.lat }}</p>
      <p>{{ user_inputs.lng}}</p>
      <p>{{ map.bounds }}</p>
    </div>
  </header>

  <main>
    <div id="map"></div>
    <l-map
      ref="myMap"
      :bounds="this.map.bounds"
      :center="[this.user_inputs.lat, this.user_inputs.lng]"
      style="height:100%; width:100%"
    >
      <l-tile-layer :url="this.map.url" :attribution="this.map.attribution"></l-tile-layer>
      <l-marker :lat-lng="[user_inputs.lat, user_inputs.lng]" @move="updateBounds"></l-marker>
      <l-circle
        :lat-lng="[user_inputs.lat, user_inputs.lng]"
        :radius="(user_inputs.distance / 2)"
        :color="colours.circle"
      ></l-circle>
      <l-circle
        ref="outsideCircle"
        :lat-lng="[user_inputs.lat, user_inputs.lng]"
        :radius="(50 + (user_inputs.distance / 2))"
        :color="colours.circle"
        :opacity="0"
      ></l-circle>
    </l-map>
  </main>
</template>

<style>
@import "./assets/base.css";
body {
  padding: 0;
  margin: 0;
}
html,
body,
#myMap {
  height: 100%;
  width: 100vw;
}
#app {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem;

  font-weight: normal;
}

header {
  line-height: 1.5;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

a,
.green {
  text-decoration: none;
  color: hsla(160, 100%, 37%, 1);
  transition: 0.4s;
}

@media (hover: hover) {
  a:hover {
    background-color: hsla(160, 100%, 37%, 0.2);
  }
}

@media (min-width: 1024px) {
  body {
    display: flex;
    place-items: center;
  }

  #app {
    display: grid;
    grid-template-columns: 1fr 1fr;
    padding: 0 2rem;
  }

  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  .logo {
    margin: 0 2rem 0 0;
  }
}
</style>
