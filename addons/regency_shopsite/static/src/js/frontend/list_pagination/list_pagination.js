/** @odoo-module **/
import "./store";

const { Component, UseState } = owl;
import { useStore } from "@fe_owl_base/js/main";

const FIRST_PAGE = 1

export class ListPaginationComponent extends Component {
    setup() {
        this.store = useStore();
    }

    get numberOfPages() {
        return this.store.catalogData.numberOfPages
    }

    get model() {
        return this.store.catalogData.model
    }

    get currentPage() {
        return this.store.catalogData.page;
    }

    get count() {
        return this.store.catalogData.count;
    }

    get limit() {
        return this.store.catalogData.limit;
    }

    get isFirstCurrentPage() {
        return this.currentPage === FIRST_PAGE
    }

    get isLastCurrentPage() {
        return this.currentPage === this.numberOfPages
    }

    onClickPageBtn(pageNumber, event) {
        let isNotOutOfRange = pageNumber > 0 && pageNumber <= this.numberOfPages
        if (isNotOutOfRange) {
            this.changePage(pageNumber, () => {
                scrollListToTop();
            })
        }
    }

    leftPages() {
        let pages = [1];
        if (this.store.currentPage <= this.props.pageOffset * 2) {
            pages = this.arrayFromRange(1, this.store.currentPage + this.props.pageOffset);
        }
        return pages;
    }

    centerPages() {
        let pages = false;
        if (this.store.currentPage > this.props.pageOffset * 2 && this.store.currentPage <= this.store.numberOfPages - this.props.pageOffset * 2) {
            pages = this.arrayFromRange(this.store.currentPage - this.props.pageOffset, this.store.currentPage + this.props.pageOffset);
        }
        return pages;
    }

    rightPages() {
        let pages = [this.store.numberOfPages];
        if (this.store.currentPage > this.store.numberOfPages - this.props.pageOffset * 2) {
            pages = this.arrayFromRange(this.store.currentPage - this.props.pageOffset, this.store.numberOfPages);
        }
        return pages;
    }

    arrayFromRange(min, max) {
        return Array.from({ length: max - min + 1 }, (a, e) => e + min);
    }

    async changePage(pageNumber, callback) {
        await this.store.catalogData.updateListData(pageNumber, this.model);
        if (callback) {
            callback();
        }
    }
}

ListPaginationComponent.defaultProps = {
    pageOffset: 2,
    localPagination: false,
}
ListPaginationComponent.props = {
    listKey: {
        type: String,
    },
    pageOffset: {
        type: Number,
    },
    localPagination: {
        type: Boolean,
    },
}

ListPaginationComponent.template = 'list_pagination';

function scrollListToTop() {
    let list = document.querySelector('#wrap');
    if (list) {
        list.scrollIntoView({ block: 'start', behavior: 'auto' });
    }
}

export {
    scrollListToTop
}
