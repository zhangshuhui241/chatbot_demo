<template>
  <p class="header-text"><b style="font-size: 200%;">Chatbot test </b> by RayZhang & Doris</p>

  <div class="conversation-history-box">
        <textarea id="textarea-history-text" type="scrolling-textbox" placeholder="conversation history here">{{history_text}}</textarea>
    </div>

    <div class="user-input-box">
        <form style="width: 100%; height: 100%;">
            <label class="input-box-label" for="textarea-user-input">User input</label>
            <textarea id="textarea-user-input" type="scrolling-textbox" class="input-text-area" v-model="user_input_text">
              {{ user_input_text }}
            </textarea>
            <button type="button" class="send-button" v-on:click="click_send">send</button>
        </form>
    </div>

</template>


<script>
export default {
  data() {
    return {
      history_text:"",
      user_input_text:""
    }
  },
  methods:{
    click_send() {
      if (this.user_input_text.trim().length>=1) {
        this.history_text = this.history_text + "\n\nuser:" + this.user_input_text
        this.user_input_text = ""
      } else {
        alert('input text can not be blank')
      }
      
    },
  }
}
</script>
