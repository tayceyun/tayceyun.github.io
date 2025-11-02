## 封装 axios

```typescript
import axios from 'axios';
import type `{ AxiosInstance, AxiosRequestConfig, AxiosResponse }` from 'axios';

interface IAxiosRequestConfig extends AxiosRequestConfig {
  interceptors?: {
    requestSuccessFn?: (config: AxiosRequestConfig) => AxiosRequestConfig;
    requestFailFn?: (err: any) => any;
    responseSuccessFn?: (res: AxiosResponse) => AxiosResponse;
    responseFailFn?: (err: any) => any;
  };
}

// ts封装axios
class AxiosRequest {
  instance: AxiosInstance;
  constructor(config: IAxiosRequestConfig) {
    this.instance = axios.create(config);
    // 可以统一添加拦截器,也可以通过对不同的实例是否传入拦截器来决定是否进行精细化拦截
    this.instance.interceptors.request.use(
      (config) => {
        // 统一设置token
        return config;
      },
      (err) => {
        // 请求失败拦截
        return err;
      }
    );
    this.instance.interceptors.response.use(
      (res) => {
        // 全局响应成功拦截
        return res;
      },
      (err) => {
        // 响应失败拦截
        return err;
      }
    );

    this.instance.interceptors.request.use(
      config.interceptors?.requestSuccessFn,
      config.interceptors?.requestFailFn
    );
    this.instance.interceptors.response.use(
      config.interceptors?.responseSuccessFn,
      config.interceptors?.responseFailFn
    );
  }

  // 封装网络请求方法
  request(config: IAxiosRequestConfig) {
    //  对第三方库进行二次封装
    // (应对库不维护时, 需要更换库的情况, 通过二次封装可以统一更换库)
    this.instance.request(config);
  }
  get() `{}`
}

// 创建实例
// 对于不同的实例通过是否传入拦截器,来进行分别处理
const sitRequest = new AxiosRequest(`{ url: '', timeout: 1000 }`);
const uatRequest = new AxiosRequest({
  url: '',
  timeout: 1000,
  interceptors: {
    requestSuccessFn: (config: AxiosRequestConfig) => {
      return config;
    },
    requestFailFn: (err: any) => {
      return err;
    },
    responseSuccessFn: (res: AxiosResponse) => {
      return res;
    },
    responseFailFn: (err: any) => {
      return err;
    }
  }
});
```
