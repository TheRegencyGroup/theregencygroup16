/** @odoo-module **/

import { ComponentWrapper } from 'web.OwlCompatibility';

const { useState, reactive } = owl;

class Store {
    state = {};
}

function createStore() {
  return reactive(new Store());
}

const env = { store: createStore() };

function useStore() {
  return useState(env.store);
}

async function mountComponentAsWidget(componentName, component) {
    let widgets = document.querySelectorAll(`[data-owl-widget=${componentName}]`);
    let mountPromises = [];
    for (let widget of widgets) {
        let props = {};
        if (component.props) {
            for (let [key, value] of Object.entries(widget.dataset)) {
                let componentPropsList = Object.keys(component.props);
                if (key.includes('Props')) {
                    let propsKey = key.slice(0, -5)
                    if (componentPropsList.includes(propsKey)) {
                        props[propsKey] = value;
                        let propsType = typeof (component.props[propsKey].type());
                        if (propsType === 'boolean') {
                            props[propsKey] = value === '1' || value === 'True';
                        } else if (propsType === 'number') {
                            props[propsKey] = +value;
                        } else if (propsType === 'array' || propsType === 'object') {
                            props[propsKey] = JSON.parse(value);
                        }
                    }
                }
            }
        }
        widget.innerHTML = '';
        let componentWrapper = new ComponentWrapper(this, component, props);
        mountPromises.push(componentWrapper.mount(widget, {position: 'first-child'}));
    }
    await Promise.all(mountPromises);
}

export {
    Store,
    useStore,
    mountComponentAsWidget,
}
