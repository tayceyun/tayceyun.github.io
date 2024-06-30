<template>
  <div>
    <div class="card-section">
      <el-card class="box-card">
        <div slot="header" class="clearfix">
          <span>快捷Link</span>
          <el-switch
            style="float: right; padding: 3px 0"
            v-model="paragraphVisible"
            active-text="工作信条"
            inactive-text=""
            @change="handleVisible"
          >
          </el-switch>
        </div>
        <div class="badges">
          <el-link href="/blog/others/why">问题总结</el-link>
          <el-link href="/blog/linklist">技术文章</el-link>
        </div>
        <el-collapse-transition>
          <div v-show="paragraphVisible" class="font">
            <el-divider></el-divider>
            💡
            想要成为优秀的开发工程师，需要通过系统地学习和总结获取知识，通过练习获取编程能力，通过工作经验来获取架构和工程能力。
            <el-divider>🔚</el-divider>
          </div>
        </el-collapse-transition>
      </el-card>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      paragraphVisible: false
    };
  },
  methods: {
    handleVisible(visible) {
      this.paragraphVisible = visible;
    }
  }
};
</script>
<style>
.box-card {
  width: 50%;
}

.card-section {
  display: flex;
  justify-content: center;
}

.el-divider--horizontal {
  margin: 10px 0;
}

.el-card__header {
  padding: 5px 20px;
}

.badges {
  display: flex;
  justify-content: space-around;
}

.font {
  font-size: 14px;
}

.el-switch__label {
  color: #718aaa;
}
</style>
