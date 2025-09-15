import { toast, TypeOptions } from 'react-toastify';

type Id = string | number;
type Type = TypeOptions | undefined;
type AutoClose = boolean | number | undefined;

const AUTOCLOSE_DELAY = 3000;

/**
 * This is a util class that facilitates the use of the Toast component provided by the react-toasttify library.
 */
class Toast {
  _id: Id = '';

  /**
   * Shows the toast component.
   *
   * @param type - The toast type: 'info' | 'success' | 'warning' | 'error' | 'default'.
   * @param text - The message.
   * @param isLoading - Shows the loading mode. Default: false.
   * @param autoClose  - If true, the toast will be closed automatically after an specific time (AUTOCLOSE_DELAY). Default: true.
   */
  show(type: Type, text: string, isLoading = false, autoClose = true) {
    const ac: AutoClose = !isLoading && autoClose ? AUTOCLOSE_DELAY : false;

    if (!this._id) {
      this._id = toast(text, {
        position: 'top-center',
        type,
        autoClose: ac,
        hideProgressBar: true,
        closeOnClick: true,
        pauseOnHover: false,
        draggable: false,
        progress: 0,
        isLoading,
        closeButton: false,
      });
    } else {
      toast.update(this._id, {
        render: text,
        type,
        autoClose: ac,
        isLoading,
      });
    }
  }

  /**
   * Hides the toast component.
   */
  hide() {
    if (this._id) {
      toast.dismiss(this._id);
    }
  }
}

export default Toast;
