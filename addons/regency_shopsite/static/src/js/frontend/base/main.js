/** @odoo-module **/

import env from'web.public_env';
import { ComponentWrapper } from 'web.OwlCompatibility';

const { Store, mount } = owl;
const { whenReady } = owl.utils;

const StoreActions = {};
const StoreState = {};
env.store = new Store({
    env,
    actions: StoreActions,
    state: StoreState,
});

function addStore(actions, state) {
    Object.assign(env.store.actions, actions);
    Object.assign(env.store.state, state);
}

function debugLog() {
    if (odoo.debug !== "1" && odoo.debug !== "assets") {
        return;
    }
    console.log.call(null, ...arguments);
}

async function loadTemplate(url) {
    let result = await fetch(url);
    if (!result.ok) {
        throw new Error("Error fetching template " + url);
    }
    let template = await result.text();
    template = template.replace(/<!--[\s\S]*?-->/g, "");
    await env.qweb.addTemplates(template);
}

function moduleVersion(template) {
    for (let k in FE_OWL_BASE_TEMPLATE_VERSIONS) {
        let prefix = template.substring(0, k.length + 1);
        if (prefix === ("/" + k)) {
            return FE_OWL_BASE_TEMPLATE_VERSIONS[k];
        }
    }
    return ""
}

async function loadTemplates(templates) {
    debugLog("loading templates");
    let promises = [];
    for (let t of templates) {
        debugLog("loading template " + t);
        promises.push(loadTemplate(t + "?v=" + moduleVersion(t)));
    }
    await Promise.all(promises);
    // await env.qweb.forceUpdate();
}

let loadTemplatesPromise = whenReady(async () => {
    if (FE_OWL_TEMPLATES) {
        await loadTemplates(FE_OWL_TEMPLATES);
    }
});

async function mountComponentAsWidget(componentName, component) {
    await loadTemplatesPromise;
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
        // widget.innerHTML = '';
        // mountPromises.push(mount(component, {props: props, target: widget}));
    }
    await Promise.all(mountPromises);
}

export {
    env,
    loadTemplates,
    debugLog,
    addStore,
    mountComponentAsWidget,
}
