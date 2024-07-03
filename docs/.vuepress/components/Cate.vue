<template>
  <div>
    <el-alert type="info" style="margin-bottom: 24px">
      <template #title>
        <a href="/blog/others/why" :underline="false">
          【❓问题聚集地🙋‍♀️】寻找问题的答案
        </a>
        <i class="el-icon-s-promotion"></i>
      </template>
    </el-alert>
    <div class="all-page">
      <el-card class="box-card" shadow="hover" v-for="(item, i) in list">
        <el-collapse
          class="collapse"
          :key="`${item.key}-collapse`"
          v-model="activeNames[i]"
        >
          <el-collapse-item v-for="(col, i) in item" :name="i">
            <template slot="title">
              <span class="title">{{ col.title }}</span>
              <el-tag
                v-for="tag in col.tagList"
                size="mini"
                :type="getTagType()"
                class="tag"
                >{{ tag }}</el-tag
              >
            </template>

            <template v-for="file in col.files">
              <el-divider
                v-if="file.type === 'divider'"
                content-position="left"
                >{{ file.name }}</el-divider
              >
              <el-link v-else :href="file.link" :underline="false">
                {{ file.name }}
              </el-link>
            </template>
          </el-collapse-item>
        </el-collapse>
      </el-card>
    </div>
  </div>
</template>

<script>
import { cateList } from '../config/index';
export default {
  data() {
    return {
      activeNames: [
        [0, 1, 2, 3, 4, 5],
        [0, 1, 2, 3, 4, 5]
      ],
      tagColorList: ['', 'info', 'warning', 'danger', 'success'],
      list: cateList
    };
  },
  methods: {
    handleClick() {
      console.log(111);
      console.log(this.tagColorList);
    },
    getTagType() {
      const index = (Math.random() * this.tagColorList.length) | 0;
      return this.tagColorList.slice(index, index + 1)[0];
    }
  }
};
</script>
<style scoped>
.all-page {
  display: flex;
}

.box-card {
  height: 100%;
  width: calc(50% - 16px);

  &:first-child {
    margin-right: 32px;
  }
}
.collapse {
  width: 100%;
}
.title {
  font-weight: 600;
  margin-right: 10px;
  font-size: 16px;
}
.tag {
  margin-right: 10px;
}
.el-link {
  display: block;
}
.el-divider--horizontal {
  margin: 8px 0;
  color: red;
}

.el-divider__text {
  color: #85888e;
  font-style: italic;
  font-size: 12px;
}
</style>
