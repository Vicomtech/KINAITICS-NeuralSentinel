<template>
  <router-view />
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: rgb(3, 37, 100);;
  display: block;
  margin: 0px;
  height: 100vh;
}

.button {
  position: relative;
  background-color: white;
  color: rgb(3, 37, 100);
  border: 2px solid rgb(3, 37, 100);
  border-radius: 4px;
  font-size: 1rem;
  font-family: Garamond, serif;
  font-weight: bolder;
  padding: 5px;
  width: fit-content;
  text-align: center;
  transition-duration: 0.4s;
  text-decoration: none;
  overflow: hidden;
  cursor: pointer;
}

.button:after {
  content: "";
  background: rgb(216, 229, 252);
  display: block;
  position: absolute;
  padding-top: 300%;
  padding-left: 350%;
  margin-left: -20px !important;
  margin-top: -120%;
  opacity: 0;
  transition: all 0.8s;
}

.button:active:after {
  padding: 0;
  margin: 0;
  opacity: 1;
  transition: 0s;
}

.button:hover {
  background-color: rgb(3, 37, 100);
  color: white;
}

body{
  margin: 0px;
  padding: 0px;
}

h2 {
  font-family: Garamond, serif;
  font-weight: bolder;
  margin-inline: 5%;
  margin-block: auto;
  text-align: left;
  font-size: 2rem;
}

h4 {
  font-family: Garamond, serif;
  font-weight: bolder;
  margin-inline: 5%;
  margin-block: 1rem;
  text-align: left;
  font-size: 1.5rem;
}

input {
  width: 10%;
}

input[type="number"]{
  margin-right: 1rem;
}

input[type="radio"] {
 margin-top:0.25rem;
 margin-inline: 0px;
 height: fit-content;
 margin-left: 1rem;
 accent-color:rgb(3, 37, 100);
}

label{
  height: fit-content;
  font-family: Garamond, serif;
  margin-inline: 0.25rem;
  font-size: 1.2rem;
}

table {
  table-layout: fixed;
  font-family: arial, sans-serif;
  border-collapse: collapse;
  margin-block: 3.5vh;
}

td,
th {
  border: 1px solid #dddddd;
  text-align: left;
  padding-left: 5px;
  font-size: 0.9rem;
  width: 10%;
}

tfoot {
  border: 4px solid #dddddd;
  font-size: 1.2vw;
  font-weight: bolder;
}

tfoot td {
  padding: 0px;
}

</style>
