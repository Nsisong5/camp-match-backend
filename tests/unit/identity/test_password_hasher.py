from camp_match.modules.identity.adapters.security.password_hasher import ScryptPasswordHasher


def test_hash_and_verify_success():
    hasher = ScryptPasswordHasher()
    password = "secure_password"
    
    encoded_hash = hasher.hash(password)
    
    assert encoded_hash.startswith("scrypt$")
    assert hasher.verify(password, encoded_hash) is True

def test_verify_failure_wrong_password():
    hasher = ScryptPasswordHasher()
    password = "secure_password"
    wrong_password = "wrong_password"
    
    encoded_hash = hasher.hash(password)
    
    assert hasher.verify(wrong_password, encoded_hash) is False

def test_hashes_are_different_for_same_password():
    hasher = ScryptPasswordHasher()
    password = "secure_password"
    
    hash1 = hasher.hash(password)
    hash2 = hasher.hash(password)
    
    assert hash1 != hash2

def test_verify_failure_malformed_hash():
    hasher = ScryptPasswordHasher()
    
    assert hasher.verify("password", "invalid_hash") is False
    assert hasher.verify("password", "scrypt$n=16384,r=8,p=1$salt$hash") is False  # valid shape but invalid b64 maybe

def test_different_parameters_still_verify():
    hasher1 = ScryptPasswordHasher(n=4096)
    hasher2 = ScryptPasswordHasher(n=8192)
    password = "password"
    
    hash1 = hasher1.hash(password)
    hash2 = hasher2.hash(password)
    
    # Both should verify regardless of current hasher's default params because params are in the hash string
    assert hasher2.verify(password, hash1) is True
    assert hasher1.verify(password, hash2) is True
