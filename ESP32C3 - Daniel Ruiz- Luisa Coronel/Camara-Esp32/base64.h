#ifndef BASE64_H
#define BASE64_H

#include <Arduino.h>

namespace base64 {
  const char chars[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

  String encode(uint8_t const* buf, unsigned int bufLen) {
    String out;
    int i;
    for (i = 0; i < bufLen;) {
      uint32_t octet_a = i < bufLen ? buf[i++] : 0;
      uint32_t octet_b = i < bufLen ? buf[i++] : 0;
      uint32_t octet_c = i < bufLen ? buf[i++] : 0;

      uint32_t triple = (octet_a << 16) + (octet_b << 8) + octet_c;

      out += chars[(triple >> 18) & 0x3F];
      out += chars[(triple >> 12) & 0x3F];
      out += i > (bufLen + 1) ? '=' : chars[(triple >> 6) & 0x3F];
      out += i > bufLen ? '=' : chars[triple & 0x3F];
    }
    return out;
  }
}

#endif
