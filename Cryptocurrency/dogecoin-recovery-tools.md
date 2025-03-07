# Detailed Guide to Dogecoin Recovery Tool Usage

This guide provides explicit instructions for using recovery tools with Dogecoin wallets. **Important**: Only use these tools on wallets you legitimately own or have legal authorization to recover.

## BTCRecover

BTCRecover is an open-source password recovery tool that works with Dogecoin Core wallets due to their shared codebase with Bitcoin.

### Setup and Installation

1. **Download the tool**:
   ```bash
   git clone https://github.com/3rdIteration/btcrecover.git
   cd btcrecover
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Recovery Process for Dogecoin Core wallet.dat

1. **Make a copy of your wallet.dat file** and work only with the copy.

2. **Extract the wallet hash** (optional but speeds up the process):
   ```bash
   python extract-scripts/extract-wallet-data.py --data-extract --wallet-type dogecoin-core path/to/wallet.dat
   ```
   This creates a .extract file that contains the wallet hash but not private keys.

3. **Basic password recovery** when you remember parts of the password:
   ```bash
   python btcrecover.py --wallet path/to/wallet.dat --wallet-type dogecoin-core
   ```

4. **Adding password hints** (when you remember parts of the password):
   ```bash
   python btcrecover.py --wallet path/to/wallet.dat --wallet-type dogecoin-core --passwordlist common_passwords.txt --typos-case --typos-swap --typos-delete
   ```

5. **Using token-based recovery** (building passwords from known components):
   ```bash
   python btcrecover.py --wallet path/to/wallet.dat --wallet-type dogecoin-core --tokenlist tokens.txt
   ```
   
   Example `tokens.txt` file:
   ```
   Dog%N
   Coin%N
   %W@%N
   ```
   This tries combinations like Dog1, Dog2, Coin1, etc.

6. **Enabling GPU acceleration** (dramatically improves speed):
   ```bash
   python btcrecover.py --wallet path/to/wallet.dat --wallet-type dogecoin-core --enable-gpu
   ```

### Performance Expectations

- Password complexity significantly impacts recovery time
- Simple passwords (under 8 characters): Minutes to hours
- Complex passwords with known patterns: Hours to days
- Random complex passwords with no hints: Could be infeasible
- GPU acceleration can provide 10-100x speedup vs CPU

## Hashcat

Hashcat is a more advanced password recovery tool that requires extracting the password hash first.

### Setup and Installation

1. **Download and install Hashcat** from [https://hashcat.net/hashcat/](https://hashcat.net/hashcat/)

2. **Install appropriate GPU drivers** for maximum performance (NVIDIA or AMD)

### Preparing Dogecoin Wallet for Hashcat

1. **Extract the hash** using specialized tools:
   
   First extract hash from wallet.dat using a tool like Wallet Key Tool:
   ```bash
   python extract_hash.py path/to/wallet.dat > hash.txt
   ```

2. **Identify hash type** - Dogecoin Core uses format 11300 (Bitcoin/Litecoin wallet.dat)
   
### Running Recovery Attacks

1. **Dictionary attack** (testing against a wordlist):
   ```bash
   hashcat -m 11300 -a 0 hash.txt wordlist.txt
   ```

2. **Rule-based attack** (applying variations to words):
   ```bash
   hashcat -m 11300 -a 0 hash.txt wordlist.txt -r rules/best64.rule
   ```

3. **Brute force attack** (for short passwords):
   ```bash
   hashcat -m 11300 -a 3 hash.txt ?a?a?a?a?a?a?a?a
   ```
   This tries all combinations of 8 characters.

4. **Mask attack** (when you know the password pattern):
   ```bash
   hashcat -m 11300 -a 3 hash.txt Doge?d?d?d?d
   ```
   This tries patterns like Doge1234, Doge5678, etc.

5. **Hybrid attack** (combining words and patterns):
   ```bash
   hashcat -m 11300 -a 6 hash.txt wordlist.txt ?d?d?d?d
   ```
   This appends 4 digits to each word in the wordlist.

### Hardware Considerations

- Modern GPUs dramatically outperform CPUs for password recovery
- NVIDIA RTX 3080/3090/4090 provides excellent performance
- Multiple GPUs can work in parallel for faster results
- Expected speeds (password attempts per second):
  - CPU: ~500-2,000 attempts/second
  - Mid-range GPU: ~25,000-100,000 attempts/second
  - High-end GPU: ~100,000-500,000 attempts/second

## Wallet-Key-Tool

Wallet-Key-Tool helps verify you're working with the correct wallet by extracting public addresses.

### Installation

```bash
git clone https://github.com/prof7bit/wallet-key-tool.git
cd wallet-key-tool
```

### Usage for Dogecoin Core

1. **View wallet information**:
   ```bash
   java -jar wallet-key-tool.jar path/to/wallet.dat
   ```
   This displays public addresses without requiring the password.

2. **Export public addresses**:
   ```bash
   java -jar wallet-key-tool.jar path/to/wallet.dat > addresses.txt
   ```

## MultiDoge Wallet Recovery

MultiDoge uses a different format than Dogecoin Core.

### Using the Built-in Recovery

1. Open MultiDoge (install if needed)
2. Go to Tools → Import Private Keys
3. Select your .wallet file or use "Import from private key text" if you have the keys written down

### Password Recovery for MultiDoge

1. **Using BTCRecover**:
   ```bash
   python btcrecover.py --wallet path/to/wallet.wallet --wallet-type multidoge
   ```

2. **More specific search with tokens**:
   ```bash
   python btcrecover.py --wallet path/to/wallet.wallet --wallet-type multidoge --tokenlist tokens.txt
   ```

## Important Recovery Tips

### Optimizing Your Recovery Attempts

1. **Start with what you know**: Use all available information about potential passwords
2. **Try shorter password attempts first**: Configure tools to try shorter combinations before longer ones
3. **Use common patterns**: People often use patterns like:
   - Base word + year (Doge2021)
   - Name + special char + number (John!42)
   - Common substitutions (a→4, e→3, i→1, o→0)

### Creating Effective Token Lists

Token lists can dramatically increase recovery speed by focusing on likely patterns:

```
# Example token list for BTCRecover
%W    # base words from wordlist
%W%d  # word + single digit
%W%d%d  # word + two digits
%W_%d%d  # word + underscore + two digits
%d%d%d%d  # four digits (like a year)
```

### Speed Optimization

1. **For MultiDoge**: Start with "--blockchain-secondsperblock 60" parameter to speed up verification
2. **For Dogecoin Core**: Use the extracted hash file instead of the full wallet when possible
3. **GPU Tuning**: Use "--gpu-temp-abort=95 --gpu-temp-retain=80" to prevent overheating

### Recovery Services (Last Resort)

If DIY recovery isn't working, specialized services exist but use with extreme caution:

1. Verify reputation extensively before sharing any files
2. Never share your entire wallet, only the encrypted hash
3. Use escrow services if available
4. Expect to pay 10-20% of recovered funds
5. Get a clear agreement in writing before proceeding

## Legal and Ethical Considerations

- Password recovery tools can be misused for unauthorized access
- Only attempt recovery on wallets you legitimately own
- In some jurisdictions, using these tools may require proper documentation of ownership
- Keep records proving you are the legitimate owner of the wallet

Remember: These tools are powerful and should be used responsibly. They are designed to help legitimate owners recover access, not to gain unauthorized access to others' funds.
