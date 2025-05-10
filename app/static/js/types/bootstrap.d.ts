declare global {
  interface Window {
    bootstrap: {
      Modal: new (element: Element, options?: any) => {
        show: () => void;
        hide: () => void;
        toggle: () => void;
        dispose: () => void;
      };
      Tooltip: new (element: Element, options?: any) => any;
      Popover: new (element: Element, options?: any) => any;
      Toast: new (element: Element, options?: any) => any;
      Alert: new (element: Element) => any;
      Button: new (element: Element) => any;
      Carousel: new (element: Element, options?: any) => any;
      Collapse: new (element: Element, options?: any) => any;
      Dropdown: new (element: Element, options?: any) => any;
      Offcanvas: new (element: Element, options?: any) => any;
      Tab: new (element: Element) => any;
    };
  }
}

export {}; 