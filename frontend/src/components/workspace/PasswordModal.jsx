import React, { useState } from "react";
import { Lock, Eye, EyeOff, KeyRound } from "lucide-react";
import { Dialog, DialogHeader, DialogTitle, DialogDescription, DialogContent, DialogFooter } from "../ui/dialog";
import { Button } from "../ui/button";

export function PasswordModal({ open, onClose, onSubmitPassword, fileName }) {
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (password.trim()) {
      onSubmitPassword(password);
      setPassword("");
      onClose();
    }
  };

  return (
    <Dialog open={open} onClose={onClose} className="max-w-md">
      <form onSubmit={handleSubmit}>
        <DialogHeader>
          <div className="w-10 h-10 rounded-full bg-brass-surface border border-brass/40 flex items-center justify-center mb-2">
            <Lock className="w-5 h-5 text-brass" />
          </div>
          <DialogTitle>Unlock Encrypted PDF</DialogTitle>
          <DialogDescription>
            The document <span className="text-ivory font-mono break-all">{fileName}</span> is protected with a password.
          </DialogDescription>
        </DialogHeader>

        <DialogContent className="space-y-4">
          <div>
            <label className="block text-xs font-mono uppercase tracking-wider text-taupe mb-1.5">
              Decryption Password
            </label>
            <div className="relative">
              <input
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoFocus
                placeholder="Enter password..."
                className="w-full px-3.5 py-2.5 bg-carbon-950 border border-slate-border focus:border-gold-500 focus:outline-none rounded-sm text-ivory placeholder:text-dim font-mono text-sm pr-10"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-taupe hover:text-ivory focus:outline-none"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>
        </DialogContent>

        <DialogFooter>
          <Button type="button" variant="ghost" size="sm" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" variant="default" size="sm" disabled={!password.trim()}>
            <KeyRound className="w-3.5 h-3.5 mr-1.5" />
            Unlock & Apply
          </Button>
        </DialogFooter>
      </form>
    </Dialog>
  );
}
