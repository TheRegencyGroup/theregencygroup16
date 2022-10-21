// /** @odoo-module **/
//
// import { extendStore, useState } from "@fe_owl_base/js/main";
// const CHANGE_PAGE = 'changeListPage';
// const UpdateFunctions = {};
//
// function addUpdateFunction (f) {
//     Object.assign(UpdateFunctions, f);
// }
//
// const actions = {
//     async [CHANGE_PAGE] ({state}, listKey, pageNumber, callback) {
//         await UpdateFunctions[listKey].call(this, state, listKey, {
//             page: pageNumber,
//         });
//         if (callback) {
//             callback();
//         }
//     },
// }
//
// // extendStore({actions})
//
// export {
//     CHANGE_PAGE,
//     addUpdateFunction
// }