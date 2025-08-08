# 파일 트리
## requirements.txt
- pip 패키지 다운로드
```bash
pip install -r requirements.txt
```
## config
- django 상위 페이지

## public
- static/media 폴더

## apps
- 앱 생성 디렉토리

# Class Diagram
```mermaid
classDiagram
    class User {
        - name: String
        - createDate: Date
        - birthday: Date
        - gender: String
        - grade: String
        - recentView: List<Item>
        - pointBalance: Double
        + login()
        + logout()
        + register()
        + withdraw()
    }
    
    class MyPage {
        - orderHistory: List<Order>
        - userComments: List<Comment>
        - inquiries: List<Inquiry>
        - notifications: List<String>
        + viewOrderHistory()
        + viewUserInfo()
        + viewComments()
        + viewInquiries()
    }
    
    class Cart {
        - items: List<Item>
        - totalPrice: Double
        - status: String
        + addItem()
        + removeItem()
        + updateQuantity()
    }
    
    class Order {
        - orderList: List<Item>
        - total: Double
        - deliveryFee: Double
        - deliveryStatus: String
        - requestMessage: String
        + placeOrder()
        + cancelOrder()
    }
    
    class Store {
        - name: String
        - address: String
        - phoneNumber: String
        - likes: Integer
        - mapApi: Map
        + viewMenu()
        + getStoreInfo()
    }
    
    class Item {
        - name: String
        - price: Double
        - description: String
    }
    
    class Comment {
        - rating: Integer
        - text: String
        - author: User
        + createComment()
        + deleteComment()
    }
    
    class Address {
        - street: String
        - city: String
        - zipCode: String
        - isPrimary: Boolean
    }
    
    class PaymentMethod {
        - type: String
        - maskedInfo: String
    }
    
    class Coupon {
        - name: String
        - discountValue: Double
        - expirationDate: Date
        - isUsed: Boolean
    }

    User "1" -- "1" MyPage
    User "1" -- "1..*" Order
    User "1" -- "1" Cart
    User "1" -- "0..*" Address
    User "1" -- "0..*" PaymentMethod
    User "1" -- "0..*" Coupon

    Cart "1" -- "*" Item
    Order "1" -- "*" Item
    Order "1" -- "1" Address
    Order "1" -- "1" PaymentMethod
    Order "1" -- "0..1" Coupon

    Store "1" -- "*" Item
    Store "1" -- "*" Comment
    User "1" -- "*" Comment
```

# 결제 순서도
```mermaid
flowchart TD
    A[사용자] --> B{메뉴 선택 및 장바구니 추가};
    B --> C{장바구니 확인};
    C --수정--> B;
    C --주문--> D[주문 페이지];
    D --> E{주문 정보 입력};
    E --주소/요청 사항--> F{쿠폰/포인트 적용};
    F --> G{최종 금액 확인};
    G --결제--> H[결제 수단 선택];
    H --> I{결제 정보 입력};
    I --> J[결제 진행];
    J --결제 실패--> H;
    J --결제 성공--> K[주문 완료];
    K --> L[주문 내역 확인];
```
순서도 설명:

- 시작: 사용자가 메뉴를 선택합니다.

- 의사 결정: 장바구니에서 메뉴를 수정할지, 바로 주문할지 결정합니다.

- 주문 페이지: 배달 정보와 할인 정보를 입력하는 단계입니다.

- 결제: 결제 수단과 정보를 입력하고 결제를 시도합니다.
 
- 분기점: 결제 성공 여부에 따라 다음 단계가 나뉩니다.
 
- 종료: 결제가 완료되면 주문 내역을 확인할 수 있습니다.

# 결제 시퀀스 다이어그램
```mermaid
sequenceDiagram
    participant User
    participant FrontEnd
    participant BackEnd
    participant PaymentGateway
    participant Database

    User->>FrontEnd: 메뉴 선택 및 장바구니 추가
    FrontEnd->>BackEnd: /cart/add 요청
    BackEnd->>Database: 장바구니 정보 저장
    Database-->>BackEnd: 성공 응답
    BackEnd-->>FrontEnd: 장바구니 업데이트
    
    User->>FrontEnd: '주문하기' 버튼 클릭
    FrontEnd->>BackEnd: /order/create 요청
    BackEnd->>BackEnd: 최종 금액 계산(쿠폰, 배달비)
    BackEnd->>FrontEnd: 주문 정보 응답
    
    User->>FrontEnd: 결제 수단 선택 및 '결제' 버튼 클릭
    FrontEnd->>PaymentGateway: 결제 요청(결제 정보, 금액)
    PaymentGateway-->>FrontEnd: 결제 결과 응답
    
    alt 결제 성공
        FrontEnd->>BackEnd: /order/complete 요청
        BackEnd->>Database: 주문 상태 업데이트
        Database-->>BackEnd: 성공 응답
        BackEnd-->>FrontEnd: 주문 완료 응답
        FrontEnd->>User: '주문이 완료되었습니다' 메시지 표시
    else 결제 실패
        FrontEnd->>User: '결제 실패' 메시지 표시
    end
```
시퀀스 다이어그램 설명:

- 메뉴 선택: 사용자가 메뉴를 선택하면 프론트엔드가 백엔드에 장바구니 추가 요청을 보냅니다.
 
- 주문 생성: 주문하기 버튼을 누르면 백엔드에서 최종 금액을 계산하고 주문 정보를 준비합니다.
 
- 결제 요청: 프론트엔드가 결제 게이트웨이에 직접 결제를 요청하고, 그 결과를 받습니다.
 
- 결과 반영: 결제 성공 시, 백엔드에 최종 주문 완료를 알리고 데이터베이스에 상태를 업데이트합니다. 결제 실패 시, 사용자에게 실패 메시지를 바로 보여줍니다.


```mermaid
graph TB
    %% 메인 시스템 구조
    subgraph "🏠 메인 페이지"
        A[배너 이벤트<br/>- 이미지 자동 롤링<br/>- 터치 시 상세 페이지 이동] 
        B[추천/인기 음식점<br/>- 위치 기반 추천<br/>- 가게 정보 표시]
        C[가게 검색<br/>- 검색 입력창<br/>- 검색 결과 출력]
        D[음식점 카테고리<br/>- 한식/중식/일식/양식/디저트<br/>- 각 카테고리별 음식점 리스트]
    end

    subgraph "🎯 공통 UI 구성요소"
        subgraph "📋 헤더"
            E1[홈 아이콘]
            E2[위치 설정]
            E3[nav bar<br/>드롭다운]
            E4[검색<br/>- 입력창<br/>- 완료버튼<br/>- 필터]
            E5[마이페이지]
            E6[즐겨찾기]
            E7[장바구니]
            E8[로그인/로그아웃]
        end

        subgraph "📱 사이드바"
            F1[현재 주문 목록]
            F2[수량 조절 +/-]
            F3[삭제 버튼]
            F4[옵션 변경]
            F5[총 금액 표시]
            F6[배달비 표시]
            F7[결제 버튼]
            F8[장바구니 비우기]
        end

        subgraph "🔻 푸터"
            G1[로고]
            G2[회사 정보]
            G3[연락처]
        end
    end

    subgraph "🏪 상세 페이지"
        subgraph "📍 음식점 정보"
            H1[기본 정보<br/>- 가게명/전화번호<br/>- 운영시간<br/>- 주소/최소주문금액]
            H2[추가 정보<br/>- 사장님 공지<br/>- 원산지 정보<br/>- 사업자 정보]
        end

        subgraph "🍽️ 메뉴 및 옵션"
            I1[메뉴 종류<br/>- 대표메뉴<br/>- 인기순/가격순]
            I2[옵션 선택<br/>- 맵기 조절<br/>- 토핑 추가]
        end

        subgraph "⭐ 별점 및 리뷰"
            J1[종합 평점<br/>- 총 리뷰수<br/>- 평점 평균]
            J2[리뷰 요약<br/>- 필터 기능]
            J3[개별 리뷰<br/>- 사용자 정보<br/>- 별점/내용/사진<br/>- 사장님 댓글]
        end

        subgraph "🗺️ 지도"
            K1[음식점 위치]
            K2[거리 표시]
            K3[지도 앱 연동<br/>- 네이버/카카오]
        end
    end

    subgraph "👤 마이페이지"
        subgraph "📊 대시보드"
            L1[주문 현황<br/>- 배송 조회<br/>- 교환/반품<br/>- 상세보기]
        end

        subgraph "📋 활동 내역"
            M1[즐겨찾기]
            M2[작성한 리뷰/댓글]
            M3[최근 본 내역]
            M4[찜 리스트]
        end

        subgraph "🔐 개인 정보"
            N1[기본 정보<br/>- 이름/생년월일<br/>- 성별/가입일<br/>- 이메일/전화번호]
            N2[결제 수단 관리<br/>- 리스트 보기<br/>- 수정/삭제]
            N3[배송지 관리]
        end

        subgraph "💬 고객 지원"
            O1[1:1 문의 내역]
            O2[상품 Q&A]
            O3[공지사항]
        end

        subgraph "🎁 혜택"
            P1[쿠폰<br/>- 보유/완료/만료]
            P2[등급 혜택 안내]
        end

        subgraph "⚙️ 설정"
            Q1[로그아웃]
            Q2[회원탈퇴]
        end
    end

    subgraph "💳 주문/결제"
        subgraph "📝 주문 정보"
            R1[주소 설정]
            R2[요청사항]
            R3[메뉴 상세<br/>- 옵션변경<br/>- 갯수추가]
        end

        subgraph "💰 결제"
            S1[결제수단]
            S2[할인쿠폰]
            S3[주문내역 확인<br/>- 음식점/메뉴<br/>- 배달료/할인료<br/>- 총 결제금액]
            S4[결제하기 버튼]
        end

        subgraph "✅ 주문 완료"
            T1[배달 예상시간]
            T2[영수증 확인]
        end
    end

    %% 연결관계
    A --> H1
    B --> H1
    C --> D
    D --> H1
    
    E7 --> F1
    F7 --> R1
    
    H1 --> I1
    I1 --> I2
    I2 --> F1
    
    R3 --> S1
    S1 --> S2
    S2 --> S3
    S3 --> S4
    S4 --> T1
    T1 --> T2

    %% 스타일링
    classDef mainPage fill:#e1f5fe
    classDef common fill:#f3e5f5
    classDef detail fill:#e8f5e8
    classDef mypage fill:#fff3e0
    classDef order fill:#fce4ec

    class A,B,C,D mainPage
    class E1,E2,E3,E4,E5,E6,E7,E8,F1,F2,F3,F4,F5,F6,F7,F8,G1,G2,G3 common
    class H1,H2,I1,I2,J1,J2,J3,K1,K2,K3 detail
    class L1,M1,M2,M3,M4,N1,N2,N3,O1,O2,O3,P1,P2,Q1,Q2 mypage
    class R1,R2,R3,S1,S2,S3,S4,T1,T2 order
```

