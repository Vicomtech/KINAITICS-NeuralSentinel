<template>
  <div class="header">
    <img class="logo" :src="vicom_Url" alt="vicomtech" />
    <h2>Neural Sentinel</h2>
    <img class="logo" :src="kinatiks_Url" alt="Kinaitics" />
  </div>
  <div style="display: flex; flex-direction: row;height: auto; ">
    <div id="images" class="Maincontainer">
      <figure>
        <img class="resultim" id="org_img" :src="osrc" alt="Original" @error="(event) => {
      event.onerror = null;
      event.target.src = 'Placeholder_view_vector.png';
    }
      " />
        <figcaption>Original</figcaption>
      </figure>

      <figure>
        <img class="resultim" id="adv_img" :src="advsrc" alt="Adversarial" @error="(event) => {
      event.onerror = null;
      event.target.src = 'Placeholder_view_vector.png';
    }
      " />
        <figcaption>Adversarial</figcaption>
      </figure>

      <figure>
        <img class="resultim" id="dif_img" :src="difsrc" alt="Difference" @error="(event) => {
      event.onerror = null;
      event.target.src = 'Placeholder_view_vector.png';
    }
      " />
        <figcaption>Difference</figcaption>
      </figure>
    </div>
    <div class="Maincontainer">
      <div id="optioncontainer">
        <div class="row selectdiv">
          <label for="models">Choose a Model:</label>
          <select name="models" id="models" v-model="model">
            <option value="model 1">Model 1</option>
          </select>
          <button id="info" class="button" @click="OpenPopUp()">
            &iscr;
          </button>
        </div>
        <div class="row">
          <div class="group">
            <h4>Attack</h4>
            <div class="pairing">
              <input type="radio" id="fgsm" name="att_group" value="fgsm" checked="true"
                @input="(event) => procesattackradio(event.target.value)" />
              <label for="fgsm">FGSM</label><br />
            </div>
            <div class="pairing">
              <input type="radio" id="pgd" name="att_group" value="pgd"
                @input="(event) => procesattackradio(event.target.value)" />
              <label for="pgd">PGD</label><br />
            </div>
            <div class="pairing">
              <input type="radio" id="bin" name="att_group" value="bim"
                @input="(event) => procesattackradio(event.target.value)" />
              <label for="bin">BIM</label>
            </div>
          </div>
          <div class="group">
            <h4>Defense</h4>
            <div class="pairing">
              <input type="radio" id="nodefense" name="def_group" value="no_defense" checked="true"
                @input="(event) => procesdefenseradio(event.target.value)" />
              <label for="nodefense">No Defense</label><br />
            </div>
            <div class="pairing">
              <input type="radio" id="def1" name="def_group" value="adversarial_learning"
                @input="(event) => procesdefenseradio(event.target.value)" />
              <label for="def1">Adversarial Learning</label><br />
            </div>
            <div class="pairing">
              <input type="radio" id="def2" name="def_group" value="dimensionality"
                @input="(event) => procesdefenseradio(event.target.value)" />
              <label for="def2">Dimensionality</label>
            </div>
            <div class="pairing">
              <input type="radio" id="def3" name="def_group" value="prediction_similarity"
                @input="(event) => procesdefenseradio(event.target.value)" />
              <label for="def3">Prediction Similarity</label>
            </div>
          </div>
          <div class="group">
            <h4>Params</h4>
            <div class="pairing">
              <label for="epsilon"> Epsilon:</label>
              <input id="epsilon" type="number" v-model="epsilon" step="0.001" min="0" />
            </div>
            <div class="pairing" v-show="selectedAtt != 'fgsm'">
              <label for="step"> Step:</label>
              <input id="step" type="number" v-model="steps" min="1" />
            </div>
          </div>
        </div>
        <div id="butrow" class="row">
          <button class="button" @click="send">SEND</button>
        </div>
        <div id="tablerow" class="row">
          <table>
            <tbody>
              <tr>
                <th>Well Classified</th>
                <td>{{ well_classified }}</td>
              </tr>
              <tr>
                <th>Successful Attack</th>
                <td>{{ succesful_attack }}</td>
              </tr>
              <tr>
                <th>Similarity</th>
                <td>{{ similarity }}</td>
              </tr>
              <tr>
                <th>Grade</th>
                <td>{{ grade }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <td colspan="2">
                  <button id="footbutton" class="button" @click="OpenStats()">Show Interpretability</button>
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
  </div>
  <div class="footer">
    <a id="about" href="https://www.vicomtech.org/es/" target="_blank" rel="noopener noreferrer">{{ new
      Date().getFullYear() }} &copy; Vicomtech
    </a>
  </div>

  <div class="container" id="container">
    <div class="popUpContent" id="popUpContent">
      <h3>{{ model[0].toUpperCase() + model.substring(1) }}</h3>
      <div class="scrollable" id="scrollable">
        <p style="padding: 2%">
          Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do
          eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad
          minim veniam, quis nostrud exercitation ullamco laboris nisi ut
          aliquip ex ea commodo consequat. Duis aute irure dolor in
          reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla
          pariatur. Excepteur sint occaecat cupidatat non proident, sunt in
          culpa qui officia deserunt mollit anim id est laborum.
        </p>
        <table>
          <tbody>
            <tr>
              <th>Precision</th>
              <td>0</td>
            </tr>
            <tr>
              <th>Recall</th>
              <td>0</td>
            </tr>
            <tr>
              <th>F1 score</th>
              <td>0</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div style="display: flex; flex-direction: row-reverse; padding-right: 10px">
        <button class="popbutton" @click="ClosePopUp()">Close</button>
      </div>
    </div>
  </div>
  <div class="container" id="loaderpopup">
    <div class="popUpContent column" id="loadercontent">
      <p style="font-size: 1.5vw">
        Awaiting response for request attack: {{ selectedAtt.toUpperCase() }},
        defense: {{ selectedDefense }}, epsilon: {{ epsilon }}, steps:
        {{ selectedAtt == "fgsm" ? "" : steps }}
      </p>
      <div class="loader"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { postselection } from "../modules/apiservice";
import { uuid } from 'vue-uuid';
import kinatiks_Url from '/Kinatiks_logo.svg'
import vicom_Url from '/logo-vicom.png'

const uid = ref("")

const selectedDefense = ref("no_defense");
const selectedAtt = ref("fgsm");
const model = ref("model 1");
const steps = ref(1);
const epsilon = ref(0.0);

const osrc = ref('Placeholder_view_vector.png');
const advsrc = ref('Placeholder_view_vector.png');
const difsrc = ref('Placeholder_view_vector.png');
const intsrc = ref('Placeholder_view_vector.png');

const well_classified = ref();
const succesful_attack = ref();
const similarity = ref();
const grade = ref();

function procesattackradio(target) {
  selectedAtt.value = target;
}

async function send() {

  var popup = document.getElementById("loaderpopup");
  popup.style.visibility = "visible";

  var results = await postselection(
    uid.value,
    selectedAtt.value,
    selectedDefense.value,
    epsilon.value,
    steps.value
  );

  popup = document.getElementById("loaderpopup");
  popup.style.visibility = "hidden";

  well_classified.value = results.well_classified;
  succesful_attack.value = results.successful_attack;
  similarity.value = results.similarity
  grade.value = results.grade;

  osrc.value = results.image_info.original_name;
  advsrc.value = results.image_info.adversarial_name;
  difsrc.value = results.image_info.difference_name;
  intsrc.value = results.image_info.fig_name;
}

function procesdefenseradio(target) {
  selectedDefense.value = target;
}

function OpenPopUp() {
  var popup = document.getElementById("container");
  popup.style.visibility = "visible";
  document.getElementById("popUpContent").focus();
}
function ClosePopUp() {
  var popup = document.getElementById("container");
  popup.style.visibility = "hidden";
}

function OpenStats() {
  let url = `/${intsrc.value}`;
  const x = document.getElementById("app").clientWidth
  const y = document.getElementById("app").clientHeight
  let param = `width=${600},height=${500},left=${x / 2 - 300},top=${y / 2 - 250}`
  window.open(url, "_blank", param);
}

onMounted(() => {
  uid.value = uuid.v1();
})
</script>

<style>
.header {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  flex-wrap: wrap;
  width: 100%;
  height: 6%;
  padding: 1%;
  background-color: #ffffff;
  box-shadow: inset 0px 0px 12px 12px #c2edf5,
    inset 5px 5px 20px 20px rgb(240, 252, 255);
  align-content: center;
  align-items: center;
  border: outset 4px #bff5ff;
}

.footer {
  display: flex;
  flex-direction: row-reverse;
  justify-content: space-between;
  align-content: flex-end;
  align-items: flex-end;
  width: auto;
  height: 6%;
  padding: 1%;
}

.Maincontainer {
  display: flex;
  flex-direction: row;
  justify-content: space-around;
  flex-wrap: wrap;
  width: 50%;
}

.group {
  display: flex;
  flex-direction: column;
  width: 28%;
  height: fit-content;
  margin: 2%;
}

.pairing {
  display: flex;
  flex-direction: row;
  width: 100%;
  padding: 5%;
  align-content: center;
  align-items: center;
}

.row {
  display: flex;
  flex-direction: row;
  justify-content: center;
  padding: 1%;
  flex-wrap: wrap;
}

.column {
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  justify-items: space-around;
  align-items: center;
  align-content: center;
  padding: 1%;
  flex-wrap: wrap;
}

.resultim {
  display: flex;
  flex-shrink: 1;
  width: 100%;
  height: 90%;
}

.selectdiv {
  position: relative;
  align-content: center;
  align-items: center;
}

.loader {
  border: 16px solid #f3f3f3;
  /* Light grey */
  border-top: 16px solid rgb(3, 37, 100);
  /* Blue */
  border-radius: 50%;
  width: 120px;
  height: 120px;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

/* hide native button */
select::-ms-expand {
  display: none;
}

.container {
  visibility: hidden;
  position: absolute;
  top: 0;
  left: 0;
  background: rgba(100, 100, 100, 0.6);
  width: 100%;
  height: 100%;
  transition-duration: 0.4s;
}

.popUpContent {
  font-family: arial, sans-serif;
  visibility: inherit;
  position: relative;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: white;
  width: 60%;
  height: 55%;
  border-radius: 4px;
}

.scrollable {
  position: relative;
  width: 90%;
  height: 70%;
  margin: auto;
  text-align: justify;
  overflow-x: unset;
  overflow-y: auto;
  overflow-wrap: normal;
}

.popbutton {
  background-color: white;
  color: rgb(3, 37, 100);
  border: 2px solid rgb(3, 37, 100);
  border-radius: 4px;
  font-size: 1.2vw;
  font-family: Garamond, serif;
  font-weight: bolder;
  padding: 2px;
  width: 10%;
  text-align: center;
  text-decoration: none;
  overflow: hidden;
  cursor: pointer;
}

.popbutton:hover {
  background-color: rgb(3, 37, 100);
  color: white;
}

figure {
  display: flex;
  flex-direction: column;
  flex-shrink: 1;
  width: auto;
  height: 250px;
  border: double 4px rgb(3, 37, 100);
  margin: 1%;
  padding: 1%;
}

figcaption {
  margin-top: 0.2%;
  font-family: Garamond, serif;
  font-style: italic;
  font-weight: bold;
  font-size: 1.5vw;
}

h3 {
  background-color: rgb(3, 37, 100);
  color: white;
  padding: 5px;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
  font-size: 2.1vw;
  font-weight: bolder;
  padding: 5px;
}

#images {
  align-content: center;
  align-items: center;
}

#optioncontainer {
  display: flex;
  flex-direction: column;
  width: 100%;
  justify-content: center;
}

#butrow {
  justify-content: flex-end;
}

#about {
  font-family: arial, sans-serif;
  text-decoration: none;
  color: rgb(3, 37, 100);
}

#info {
  width: 5%;
}

#footbutton {
  width: 100%;
}
</style>
