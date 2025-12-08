/*getVisibleContent*/
const getVisibleContent = () => {
    // 定义变量存储所有可视元素+视口宽高
    const visibleElements = [];
    const viewportHeight = window.innerHeight;
    const viewportWeight = window.innerWidth;

    // 获取页面上所有元素
    const elements = document.querySelectorAll("body *");

    // 循环遍历所有元素逐个处理
    for (let i = 0; i < elements.length; i++) {
        // 获取元素的尺寸与位置
        const element = elements[i];
        const rect = element.getBoundingClientRect();

        // 判断元素的宽高，如果没有大小则跳过
        if (rect.height === 0 || rect.width === 0) continue;

        // 排除完全在当前屏幕可视区域之外的元素(上方、下方、左侧、右侧)的元素
        if (
            rect.bottom < 0 ||
            rect.top > viewportHeight ||
            rect.right < 0 ||
            rect.left > viewportWeight
        ) continue;

        // 通用样式判断当前元素是否隐藏
        const style = window.getComputedStyle(element);
        if (
            style.display === 'none' || // 块隐藏
            style.visibility === 'hidden' || // 隐藏不可见
            style.opacity === '0' // 透明度为0
        ) continue;

        // 如果element是文本节点或有意义的元素，请将其添加到结果中
        if (
            element.innerText ||
            element.tagName === "IMG" ||
            element.tagName === "INPUT" ||
            element.tagName === "BUTTON"
        ) visibleElements.push(element.outerHTML)
    }

    // 将所有内容使用空格拼接后包裹在div内返回
    return '<div>' + visibleElements.join(' ') + '</div>'
}
/*getVisibleContent*/

/*getInteractiveElements*/
const getInteractiveElements = () => {
    // 定义变量存储激活元素列表+视口宽高
    const interactiveElements = [];
    const viewportHeight = window.innerHeight;
    const viewportWidth = window.innerWidth;

    // 获取页面上所有可交互的元素，包含按钮、a标签、输入框、文本域、下拉菜单、按钮、tab等
    const elements = document.querySelectorAll('button, a, input, textarea, select, [role="button"], [tabindex]:not([tabindex="-1"])');

    // 定义变量用于生成连续的唯一索引
    let validElementIndex = 0;

    // 循环遍历所有元素
    for (let i = 0; i < elements.length; i++) {
        // 取出对应元素并获取尺寸+位置
        const element = elements[i];
        const rect = element.getBoundingClientRect();

        // 宽高任意为0则跳过这条元素
        if (rect.width === 0 || rect.height === 0) continue;

        // 视口不可见该元素则跳过
        if (
            rect.bottom < 0 ||
            rect.top > viewportHeight ||
            rect.right < 0 ||
            rect.left > viewportWidth
        ) continue;

        // 样式不可见则跳过该元素
        const style = window.getComputedStyle(element);
        if (
            style.display === 'none' ||
            style.visibility === 'hidden' ||
            style.opacity === '0'
        ) continue;


        // 获取元素的标签名并转换成小写，同时提取标签内容
        let tagName = element.tagName.toLowerCase();
        let text = '';

        // 根据标签类型不同处理不同的逻辑，首先是输入框/文本域/下拉菜单
        if (element.value && ['input', 'textarea', 'select'].includes(tagName)) {
            text = element.value;

            // 标签为输入框则执行以下代码，记录label和placeholder
            if (tagName === 'input') {
                // 查询输入框的label是否存在并赋值
                let labelText = '';
                if (element.id) {
                    const label = document.querySelector(`label[for="${element.id}"]`);
                    if (label) {
                        labelText = label.innerText.trim();
                    }
                }

                // 查找父级或同级的 label (当没有 for 属性绑定时)
                if (!labelText) {
                    const parentLabel = element.closest('label');
                    if (parentLabel) {
                        labelText = parentLabel.innerText.trim().replace(element.value, '').trim();
                    }
                }

                // 拼接label消息
                if (labelText) {
                    text = `[Label: ${labelText}] ${text}`;
                }

                // 拼接placeholder信息
                if (element.placeholder) {
                    text = `${text} [Placeholder: ${element.placeholder}]`;
                }
            }
        } else if (element.innerText) {
            // 普通元素则提取内部文本并剔除多余空格 (如 <button>提交</button>)
            text = element.innerText.trim().replace(/\\s+/g, ' ');
        } else if (element.alt) {
            // 图片按钮，取 alt 属性
            text = element.alt;
        } else if (element.title) {
            // 取 title 属性
            text = element.title;
        } else if (element.placeholder) {
            // 提取placeholder
            text = `[Placeholder: ${element.placeholder}]`;
        } else if (element.type) {
            // 兜底逻辑将元素的类型作为文本描述
            text = `[${element.type}]`;

            // 针对没有值的 Input，再次尝试获取 Label 和 Placeholder (逻辑同上)
            if (tagName === 'input') {
                let labelText = '';
                if (element.id) {
                    const label = document.querySelector(`label[for="${element.id}"]`);
                    if (label) {
                        labelText = label.innerText.trim();
                    }
                }

                if (!labelText) {
                    const parentLabel = element.closest('label');
                    if (parentLabel) {
                        labelText = parentLabel.innerText.trim();
                    }
                }

                if (labelText) {
                    text = `[Label: ${labelText}] ${text}`;
                }

                if (element.placeholder) {
                    text = `${text} [Placeholder: ${element.placeholder}]`;
                }
            }
        } else {
            // 都不满足，则设置为No text
            text = '[No text]';
        }

        // 检测文本长度是否超过100，如果是则剔除多余的部分
        if (text.length > 100) {
            text = text.substring(0, 97) + '...';
        }

        // 为当前元素添加data-manus-id的属性，值为manus-element-idx，这样可以通过索引找到对应的元素
        element.setAttribute('data-manus-id', `manus-element-${validElementIndex}`);

        // 构建css选择器
        const selector = `[data-manus-id="manus-element-${validElementIndex}"]`;

        // 将索引、标签名、文本、选择器添加到激活元素列表中
        interactiveElements.push({
            index: validElementIndex,
            tag: tagName,
            text: text,
            selector: selector
        });

        // 索引自增1
        validElementIndex++;
    }

    // 最终返回所有激活元素数据
    return interactiveElements;
}
/*getInteractiveElements*/